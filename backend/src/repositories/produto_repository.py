from decimal import Decimal
from typing import Optional
from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.configs import settings
from core.enums import ProdutoStatusEnum
from models.categoria_model import CategoriaModel
from models.entrada_model import EntradaModel
from models.estoque_model import EstoqueModel
from models.informacao_nutricional_model import InformacaoNutricionalModel
from models.lote_model import LoteModel
from models.produto_model import ProdutoModel
from models.unidade_medida_model import UnidadeMedidaModel
from schemas.produto_schema import ProdutoFilterSchema


class ProdutoRepository:
    # Expressões Calculadas
    @staticmethod
    def _estoque_total_expr():
        return (
            select(
                func.coalesce(
                    func.sum(
                        EstoqueModel.quantidade_atual
                    ),
                    Decimal("0")
                )
            )
            .select_from(LoteModel)
            .join(EntradaModel, EntradaModel.lote_id == LoteModel.id)
            .join(EstoqueModel, EstoqueModel.entrada_id == EntradaModel.id)
            .where(LoteModel.produto_id == ProdutoModel.id)
            .correlate(ProdutoModel)
            .scalar_subquery()
        )

    @staticmethod
    def _validade_expr():
        # Primeiro buscamos a menor validade de um lote que ainda possua estoque.
        validade_com_estoque = (
            select(
                func.min(LoteModel.data_validade)
            )
            .select_from(LoteModel)
            .join(EntradaModel, EntradaModel.lote_id == LoteModel.id)
            .join(EstoqueModel, EstoqueModel.entrada_id == EntradaModel.id)
            .where(LoteModel.produto_id == ProdutoModel.id, EstoqueModel.quantidade_atual > 0, LoteModel.data_validade.is_not(None))
            .correlate(ProdutoModel)
            .scalar_subquery()
        )

        # Caso o produto possua lote, mas ainda não tenha entrada/estoque, usamos a menor validade cadastrada como fallback
        validade_geral = (
            select(
                func.min(LoteModel.data_validade)
            )
            .where(LoteModel.produto_id == ProdutoModel.id, LoteModel.data_validade.is_not(None))
            .correlate(ProdutoModel)
            .scalar_subquery()
        )

        return func.coalesce(
            validade_com_estoque,
            validade_geral
        )

    @staticmethod
    def _status_expr(estoque_total, validade):
        hoje = func.current_date()
        limite_validade = func.current_date() + settings.PRODUTO_VALIDADE_ALERTA_DIAS

        return case(
            (
                estoque_total <= 0, ProdutoStatusEnum.SEM_ESTOQUE.value
            ),
            (
                and_(validade.is_not(None), validade <
                     hoje), ProdutoStatusEnum.VENCIDO.value
            ),
            (
                and_(validade.is_not(None), validade <=
                     limite_validade), ProdutoStatusEnum.PROXIMO_VENCIMENTO.value
            ),
            (
                estoque_total <= settings.ESTOQUE_BAIXO_LIMITE, ProdutoStatusEnum.ESTOQUE_BAIXO.value
            ),
            else_=ProdutoStatusEnum.OK.value
        )

    # Buscas
    @staticmethod
    async def find_by_id(db: AsyncSession, produto_id: int, with_relations: bool = False) -> Optional[ProdutoModel]:
        query = select(ProdutoModel).where(ProdutoModel.id == produto_id)

        if with_relations:
            query = query.options(
                selectinload(ProdutoModel.usuario),
                selectinload(ProdutoModel.categoria),
                selectinload(ProdutoModel.unidade_medida),
                selectinload(ProdutoModel.informacao_nutricional).selectinload(
                    InformacaoNutricionalModel.unidade_porcao)
            )

        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def find_by_name(db: AsyncSession, nome: str) -> Optional[ProdutoModel]:
        query = select(ProdutoModel).where(ProdutoModel.nome == nome)
        result = await db.execute(query)
        return result.scalars().unique().one_or_none()

    @staticmethod
    async def find_by_code(db: AsyncSession, cod_idf: str) -> Optional[ProdutoModel]:
        query = select(ProdutoModel).where(ProdutoModel.cod_idf == cod_idf)
        result = await db.execute(query)
        return result.scalars().unique().one_or_none()

    # CREATE / UPDATE
    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        cod_idf: str,
        nome: str,
        descricao: Optional[str],
        preco_venda_atual: Decimal,
        eh_perecivel: bool,
        usuario_id: int,
        categoria_id: int,
        unidade_medida_id: int,
        informacao_nutricional_id: Optional[int]
    ) -> ProdutoModel:
        produto = ProdutoModel(
            cod_idf=cod_idf,
            nome=nome,
            descricao=descricao,
            preco_venda_atual=preco_venda_atual,
            eh_perecivel=eh_perecivel,
            usuario_id=usuario_id,
            categoria_id=categoria_id,
            unidade_medida_id=unidade_medida_id,
            informacao_nutricional_id=informacao_nutricional_id
        )

        db.add(produto)
        await db.flush()

        return produto

    @staticmethod
    async def update(db: AsyncSession, produto: ProdutoModel, values: dict) -> ProdutoModel:
        for field, value in values.items():
            setattr(produto, field, value)

        await db.flush()

        return produto

    # Listagem
    @staticmethod
    async def list(db: AsyncSession, filters: ProdutoFilterSchema) -> List[ProdutoModel]:
        estoque_total = ProdutoRepository._estoque_total_expr()
        validade = ProdutoRepository._validade_expr()
        produto_status = ProdutoRepository._status_expr(
            estoque_total, validade)
        estoque_baixo = and_(
            estoque_total < 0,
            estoque_total <= settings.ESTOQUE_BAIXO_LIMITE
        )

        conditions = []

        # Nome
        if filters.nome:
            conditions.append(ProdutoModel.nome.ilike(
                f"%{filters.nome.strip()}%"))

        # Categoria por ID
        if filters.categoria_id is not None:
            conditions.append(ProdutoModel.categoria_id ==
                              filters.categoria_id)

        # Categoria por texto
        if filters.categoria:
            conditions.append(
                CategoriaModel.nome.ilike(
                    f"%{filters.categoria.strip()}%"
                )
            )

        # Preço
        if filters.preco_min is not None:
            conditions.append(
                ProdutoModel.preco_venda_atual >= filters.preco_min)

        if filters.preco_max is not None:
            conditions.append(
                ProdutoModel.preco_venda_atual <= filters.preco_max)

        # Status
        if filters.status is not None:
            conditions.append(produto_status == filters.status.value)

        # Count
        count_query = (
            select(func.count(ProdutoModel.id))
            .join(CategoriaModel, CategoriaModel.id == ProdutoModel.categoria_id)
        )

        if conditions:
            count_query = count_query.where(*conditions)

        count_result = await db.execute(count_query)

        total = count_result.scalar_one()

        # Items
        query = (
            select(
                ProdutoModel,
                CategoriaModel.nome.label("categoria_nome"),
                UnidadeMedidaModel.nome.label("unidade_nome"),
                UnidadeMedidaModel.sigla.label("unidade_sigla"),
                estoque_total.label("estoque_total"),
                validade.label("validade"),
                produto_status.label("status"),
                estoque_baixo.label("estoque_baixo")
            )
            .join(CategoriaModel, CategoriaModel.id == ProdutoModel.categoria_id)
            .join(UnidadeMedidaModel, UnidadeMedidaModel.id == ProdutoModel.unidade_medida_id)
        )

        if conditions:
            query = query.where(*conditions)

        query = (
            query.order_by(ProdutoModel.nome.asc())
            .offset((filters.page - 1) * filters.per_page)
            .limit(filters.per_page)
        )

        result = await db.execute(query)

        return result.all(), total

    # Indicadores do produto
    @staticmethod
    async def get_indicators(db: AsyncSession, produto_id: int):
        estoque_total = ProdutoRepository._estoque_total_expr()
        validade = ProdutoRepository._validade_expr()
        produto_status = ProdutoRepository._status_expr(estoque_total, validade)
        estoque_baixo = and_(estoque_total > 0, estoque_total <= settings.ESTOQUE_BAIXO_LIMITE)

        query = (
            select(
                estoque_total.label("estoque_total"),
                validade.label("validade"),
                produto_status.label("status"),
                estoque_baixo.label("estoque_baixo")
            )
            .select_from(ProdutoModel)
            .where(ProdutoModel.id == produto_id)
        )
        result = await db.execute(query)

        return result.one_or_none()