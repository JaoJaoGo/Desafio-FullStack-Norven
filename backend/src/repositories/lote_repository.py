from itertools import count
from typing import Optional
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.entrada_model import EntradaModel
from models.estoque_model import EstoqueModel
from models.produto_model import ProdutoModel
from models.lote_model import LoteModel
from schemas.lote_schema import LoteCreateSchema

class LoteRepository:
    @staticmethod
    async def list(db: AsyncSession, search, produto_id, validade_inicio, validade_fim, page, per_page):
        estoque_total = (
            select(func.coalesce(func.sum(EstoqueModel.quantidade_atual), 0))
            .select_from(EntradaModel).join(EstoqueModel, EstoqueModel.entrada_id == EntradaModel.id)
            .where(EntradaModel.lote_id == LoteModel.id).correlate(LoteModel).scalar_subquery()
        )

        conditions = []

        if search:
            value = f"%{search.strip()}%"

            conditions.append(
                or_(
                    LoteModel.numero.ilike(value),
                    ProdutoModel.nome.ilike(value)
                )
            )
        
        if produto_id:
            conditions.append(LoteModel.produto_id == produto_id)

        if validade_inicio:
            conditions.append(LoteModel.data_validade >= validade_inicio)

        if validade_fim:
            conditions.append(LoteModel.data_validade <= validade_fim)

        base = select(LoteModel).join(ProdutoModel, LoteModel.produto_id == ProdutoModel.id)

        count_query = select(func.count(LoteModel.id)).join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)

        if conditions:
            base = base.where(*conditions)
            count_query = count_query.where(*conditions)

        total = await db.execute(count_query).scalar_one()

        result = await db.execute(
            select(LoteModel, ProdutoModel.nome.label("produto_nome"), estoque_total.label("estoque_total"))
            .join(ProdutoModel, LoteModel.produto_id == ProdutoModel.id)
            .where(*conditions)
            .order_by(LoteModel.data_validade.asc().nulls_last(), LoteModel.numero.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        return result.all(), total

    @staticmethod
    async def list_by_product(db: AsyncSession, produto_id: int):
        query = select(LoteModel).filter(LoteModel.produto_id == produto_id)
        result = await db.execute(query)

        return result.scalars().all()

    @staticmethod
    async def find_by_id(db: AsyncSession, lote_id: int) -> Optional[LoteModel]:
        query = select(LoteModel).filter(LoteModel.id == lote_id)
        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def find_by_product_and_number(db: AsyncSession, produto_id: int, numero: str) -> Optional[LoteModel]:
        query = select(LoteModel).filter(LoteModel.produto_id == produto_id, LoteModel.numero == numero)
        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def exists_without_validity(db: AsyncSession, produto_id: int) -> bool:
        query = select(LoteModel.id).filter(LoteModel.produto_id == produto_id, LoteModel.data_validade.is_(None)).limit(1)
        result = await db.execute(query)

        return result.scalars().unique().one_or_none() is not None

    @staticmethod
    async def create(db: AsyncSession, data: LoteCreateSchema) -> LoteModel:
        lote = LoteModel(
            numero=data.numero,
            data_validade=data.data_validade,
            produto_id=data.produto_id
        )
        
        db.add(lote)
        await db.flush()
        
        return lote