from typing import Optional
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.entrada_model import EntradaModel
from models.estoque_model import EstoqueModel
from models.lote_model import LoteModel
from models.produto_model import ProdutoModel

class EstoqueRepository:
    @staticmethod
    async def create(db: AsyncSession, *, entrada_id: int, quantidade: object, corredor: str, prateleira: str, secao: str) -> EstoqueModel:
        estoque = EstoqueModel(
            entrada_id=entrada_id,
            quantidade=quantidade,
            corredor=corredor,
            prateleira=prateleira,
            secao=secao
        )

        db.add(estoque)
        await db.flush()

        return estoque
    
    @staticmethod
    async def find_by_id(db: AsyncSession, estoque_id: int) -> Optional[EstoqueModel]:
        query = select(EstoqueModel).options(selectinload(EstoqueModel.entrada).selectinload(EntradaModel.lote).selectinload(LoteModel.produto)).where(EstoqueModel.id == estoque_id)

        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def lock_by_id(db: AsyncSession, estoque_id: int) -> Optional[EstoqueModel]:
        result = await db.execute(select(EstoqueModel).where(EstoqueModel.id == estoque_id).with_for_update())

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def find_by_entry(db: AsyncSession, entrada_id: int) -> Optional[EstoqueModel]:
        result = await db.execute(select(EstoqueModel).where(EstoqueModel.entrada_id == entrada_id))

        return result.scalars().first()

    @staticmethod
    async def list(db: AsyncSession, search: str, produto_id: int, lote_id: int, page: int, per_page: int):
        conditions = []

        if search:
            value = f"%{search.strip()}%"

            conditions.append(
                or_(
                    ProdutoModel.nome.ilike(value),
                    LoteModel.numero.ilike(value),
                    EstoqueModel.corredor.ilike(value),
                    EstoqueModel.prateleira.ilike(value),
                    EstoqueModel.secao.ilike(value)
                )
            )

        if produto_id:
            conditions.append(ProdutoModel.id == produto_id)

        if lote_id:
            conditions.append(LoteModel.id == lote_id)

        count_query = (
            select(func.count(EstoqueModel.id))
            .join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
        )

        query = (
            select(EstoqueModel, LoteModel.id.label("lote_id"), LoteModel.numero.label("lote_numero"), ProdutoModel.id.label("produto_id"), ProdutoModel.nome.label("produto_nome"))
            .join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
        )

        if conditions:
            count_query = count_query.where(*conditions)
            query = query.where(*conditions)

        total = await db.execute(count_query).scalar_one()
        result = await db.execute(query.order_by(ProdutoModel.nome, LoteModel.numero).offset((page - 1) * per_page).limit(per_page))

        return result.all(), total

    @staticmethod
    async def list_by_product(db: AsyncSession, produto_id: int):
        query = (
            select(EstoqueModel, LoteModel.id.label("lote_id"), LoteModel.numero.label("lote_numero"), ProdutoModel.id.label("produto_id"), ProdutoModel.nome.label("produto_nome"))
            .join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
            .where(ProdutoModel.id == produto_id)
        )
        
        result = await db.execute(query)
        return result.all()

    @staticmethod
    async def update(db: AsyncSession, estoque: EstoqueModel, values: dict):
        for field, value in values.items():
            setattr(estoque, field, value)

        await db.flush()

        return estoque