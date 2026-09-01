from decimal import Decimal
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.entrada_model import EntradaModel
from models.estoque_model import EstoqueModel
from models.fornecedor_model import FornecedorModel
from models.lote_model import LoteModel
from models.produto_model import ProdutoModel
from models.saida_model import SaidaModel
from models.usuario_model import UsuarioModel

from schemas.entrada_schema import EntradaFilterSchema


class EntradaRepository:
    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        quantidade: Decimal,
        preco_custo_unitario: Decimal,
        tipo_entrada: str,
        observacao: Optional[str],
        fornecedor_id: int,
        lote_id: int,
        usuario_id: int,
        data_entrada: Optional[datetime] = None,
    ) -> EntradaModel:
        values = {
            "quantidade": quantidade,
            "preco_custo_unitario": preco_custo_unitario,
            "tipo_entrada": tipo_entrada,
            "observacao": observacao,
            "fornecedor_id": fornecedor_id,
            "lote_id": lote_id,
            "usuario_id": usuario_id,
        }

        if data_entrada is not None:
            values["data_entrada"] = data_entrada

        entrada = EntradaModel(**values)

        db.add(entrada)
        await db.flush()

        return entrada

    @staticmethod
    async def find_by_id(db: AsyncSession, entrada_id: int):
        query = select(EntradaModel).where(EntradaModel.id == entrada_id)
        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def find_detail_by_id(db: AsyncSession, entrada_id: int):
        query = (
            select(
                EntradaModel.id.label("id"),
                EntradaModel.data_entrada.label("data_entrada"),
                EntradaModel.quantidade.label("quantidade"),
                EntradaModel.preco_custo_unitario.label("preco_custo_unitario"),
                EntradaModel.tipo_entrada.label("tipo_entrada"),
                EntradaModel.observacao.label("observacao"),
                FornecedorModel.id.label("fornecedor_id"),
                FornecedorModel.nome.label("fornecedor_nome"),
                LoteModel.id.label("lote_id"),
                LoteModel.numero.label("lote_numero"),
                ProdutoModel.id.label("produto_id"),
                ProdutoModel.nome.label("produto_nome"),
                UsuarioModel.id.label("usuario_id"),
                UsuarioModel.nome.label("usuario_nome"),
                EstoqueModel.id.label("estoque_id"),
                EstoqueModel.quantidade_atual.label("quantidade_atual"),
                EstoqueModel.corredor.label("corredor"),
                EstoqueModel.prateleira.label("prateleira"),
                EstoqueModel.secao.label("secao")
            )
            .join(FornecedorModel, FornecedorModel.id == EntradaModel.fornecedor_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
            .join(UsuarioModel, UsuarioModel.id == EntradaModel.usuario_id)
            .join(EstoqueModel, EstoqueModel.entrada_id == EntradaModel.id)
            .where(EntradaModel.id == entrada_id)
            .order_by(EstoqueModel.id.asc())
            .limit(1)
        )

        result = await db.execute(query)

        return result.mappings().one_or_none()

    @staticmethod
    async def update(db: AsyncSession, entrada: EntradaModel, values: dict) -> EntradaModel:
        for field, value in values.items():
            setattr(entrada, field, value)

        await db.flush()

        return entrada

    @staticmethod
    async def get_first_exit_date(db: AsyncSession, entrada_id: int):
        query = (
            select(func.min(SaidaModel.data_saida))
            .select_from(SaidaModel)
            .join(EstoqueModel, EstoqueModel.id == SaidaModel.estoque_id)
            .where(EstoqueModel.entrada_id == entrada_id)
        )

        result = await db.execute(query)

        return result.scalar_one()

    @staticmethod
    async def list(db: AsyncSession, filters: EntradaFilterSchema):
        conditions = []

        if filters.search:
            value = f"%{filters.search.strip()}%"

            conditions.append(
                or_(
                    ProdutoModel.nome.ilike(value),
                    FornecedorModel.nome.ilike(value),
                    FornecedorModel.cnpj.ilike(value),
                    LoteModel.numero.ilike(value),
                    EntradaModel.tipo_entrada.ilike(value),
                    UsuarioModel.nome.ilike(value),
                )
            )

        if filters.produto_id is not None:
            conditions.append(ProdutoModel.id == filters.produto_id)

        if filters.fornecedor_id is not None:
            conditions.append(EntradaModel.fornecedor_id == filters.fornecedor_id)

        if filters.usuario_id is not None:
            conditions.append(EntradaModel.usuario_id == filters.usuario_id)

        if filters.tipo_entrada:
            conditions.append(EntradaModel.tipo_entrada == filters.tipo_entrada.strip().upper())

        if filters.quantidade_min is not None:
            conditions.append(EntradaModel.quantidade >= filters.quantidade_min)

        if filters.quantidade_max is not None:
            conditions.append(EntradaModel.quantidade <= filters.quantidade_max)

        if filters.data_inicio is not None:
            conditions.append(EntradaModel.data_entrada >= filters.data_inicio)

        if filters.data_fim is not None:
            conditions.append(EntradaModel.data_entrada <= filters.data_fim)

        count_query = (
            select(func.count(func.distinct(EntradaModel.id)))
            .join(FornecedorModel, FornecedorModel.id == EntradaModel.fornecedor_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
            .join(UsuarioModel, UsuarioModel.id == EntradaModel.usuario_id)
        )

        query = (
            select(
                EntradaModel.id.label("id"),
                EntradaModel.data_entrada.label("data_entrada"),
                EntradaModel.quantidade.label("quantidade"),
                EntradaModel.preco_custo_unitario.label("preco_custo_unitario"),
                EntradaModel.tipo_entrada.label("tipo_entrada"),
                EntradaModel.observacao.label("observacao"),
                FornecedorModel.id.label("fornecedor_id"),
                FornecedorModel.nome.label("fornecedor_nome"),
                LoteModel.id.label("lote_id"),
                LoteModel.numero.label("lote_numero"),
                ProdutoModel.id.label("produto_id"),
                ProdutoModel.nome.label("produto_nome"),
                UsuarioModel.id.label("usuario_id"),
                UsuarioModel.nome.label("usuario_nome"),
                EstoqueModel.id.label("estoque_id"),
                EstoqueModel.quantidade_atual.label("quantidade_atual"),
                EstoqueModel.corredor.label("corredor"),
                EstoqueModel.prateleira.label("prateleira"),
                EstoqueModel.secao.label("secao"),
            )
            .join(FornecedorModel, FornecedorModel.id == EntradaModel.fornecedor_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
            .join(UsuarioModel, UsuarioModel.id == EntradaModel.usuario_id)
            .join(EstoqueModel, EstoqueModel.entrada_id == EntradaModel.id)
        )

        if conditions:
            count_query = count_query.where(*conditions)
            query = query.where(*conditions)

        count_result = await db.execute(count_query)
        total = count_result.scalar_one()

        result = await db.execute(
            query
            .order_by(EntradaModel.data_entrada.desc(), EntradaModel.id.desc())
            .offset((filters.page - 1) * filters.per_page)
            .limit(filters.per_page)
        )

        return result.mappings().all(), total