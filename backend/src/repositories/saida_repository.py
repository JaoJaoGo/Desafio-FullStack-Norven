from typing import Optional
from sqlalchemy import cast, func, or_, select, String
from sqlalchemy.ext.asyncio import AsyncSession

from models.entrada_model import EntradaModel
from models.estoque_model import EstoqueModel
from models.lote_model import LoteModel
from models.produto_model import ProdutoModel
from models.saida_model import SaidaModel
from models.usuario_model import UsuarioModel

class SaidaRepository:
    @staticmethod
    async def create(db: AsyncSession, **values) -> SaidaModel:
        saida = SaidaModel(**values)

        db.add(saida)
        await db.flush()

        return saida

    @staticmethod
    async def find_by_id(db: AsyncSession, saida_id: int) -> Optional[SaidaModel]:
        query = (
            select(
                SaidaModel.id.label("id"),
                SaidaModel.data_saida.label("data_saida"),
                SaidaModel.quantidade.label("quantidade"),
                SaidaModel.tipo_saida.label("tipo_saida"),
                SaidaModel.preco_venda_unitario.label("preco_venda_unitario"),
                EstoqueModel.id.label("estoque_id"),
                LoteModel.id.label("lote_id"),
                LoteModel.numero.label("lote_numero"),
                ProdutoModel.id.label("produto_id"),
                ProdutoModel.nome.label("produto_nome"),
                UsuarioModel.id.label("usuario_id"),
                UsuarioModel.nome.label("usuario_nome")
            )
            .join(EstoqueModel, EstoqueModel.id == SaidaModel.estoque_id)
            .join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
            .join(UsuarioModel, UsuarioModel.id == SaidaModel.usuario_id)
            .where(SaidaModel.id == saida_id)
        )

        result = await db.execute(query)

        return result.mappings().one_or_none()

    @staticmethod
    async def update(db: AsyncSession, saida: SaidaModel, values: dict) -> SaidaModel:
        for field, value in values.items():
            setattr(saida, field, value)

        await db.flush()

        return saida

    @staticmethod
    async def list(db: AsyncSession, filters: SaidaFilterSchema) -> List[SaidaModel]:
        conditions = []

        if filters.search:
            value = f"%{filters.search.strip()}%"

            conditions.append(
                or_(
                    ProdutoModel.nome.ilike(value),
                    LoteModel.numero.ilike(value),
                    UsuarioModel.nome.ilike(value),
                    cast(SaidaModel.tipo_saida, String).ilike(value)
                )
            )

        if filters.produto_id is not None:
            conditions.append(ProdutoModel.id == filters.produto_id)

        if filters.usuario_id is not None:
            conditions.append(SaidaModel.usuario_id == filters.usuario_id)

        if filters.tipo_saida is not None:
            conditions.append(SaidaModel.tipo_saida == filters.tipo_saida)

        if filters.quantidade_min is not None:
            conditions.append(SaidaModel.quantidade >= filters.quantidade_min)

        if filters.quantidade_max is not None:
            conditions.append(SaidaModel.quantidade <= filters.quantidade_max)

        if filters.data_inicio is not None:
            conditions.append(SaidaModel.data_saida >= filters.data_inicio)

        if filters.data_fim is not None:
            conditions.append(SaidaModel.data_saida <= filters.data_fim)

        count_query = (
            select(func.count(SaidaModel.id))
            .join(EstoqueModel, EstoqueModel.id == SaidaModel.estoque_id)
            .join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
            .join(UsuarioModel, UsuarioModel.id == SaidaModel.usuario_id)
        )

        query = (
            select(
                SaidaModel.id.label("id"),
                SaidaModel.data_saida.label("data_saida"),
                SaidaModel.quantidade.label("quantidade"),
                SaidaModel.tipo_saida.label("tipo_saida"),
                SaidaModel.preco_venda_unitario.label("preco_venda_unitario"),
                EstoqueModel.id.label("estoque_id"),
                LoteModel.id.label("lote_id"),
                LoteModel.numero.label("lote_numero"),
                ProdutoModel.id.label("produto_id"),
                ProdutoModel.nome.label("produto_nome"),
                UsuarioModel.id.label("usuario_id"),
                UsuarioModel.nome.label("usuario_nome")
            )
            .join(EstoqueModel, EstoqueModel.id == SaidaModel.estoque_id)
            .join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
            .join(UsuarioModel, UsuarioModel.id == SaidaModel.usuario_id)
        )

        if conditions:
            count_query = count_query.where(*conditions)
            query = query.where(*conditions)
        
        total = await db.execute(count_query).scalar_one()
        result = await db.execute(query.order_by(SaidaModel.data_saida.desc(), SaidaModel.id.desc()).offset((filters.page - 1) * filters.page_size).limit(filters.page_size))

        return result.mappings().all(), total