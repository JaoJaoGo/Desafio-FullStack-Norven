from decimal import Decimal
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
    async def create(db: AsyncSession, *, entrada_id: int, quantidade: Decimal, corredor: str, prateleira: str, secao: str) -> EstoqueModel:
        estoque = EstoqueModel(
            entrada_id=entrada_id,
            quantidade_atual=quantidade,
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
    async def find_detail_by_id(db: AsyncSession, estoque_id: int):
        query = (
            select(
                EstoqueModel.id.label("id"),
                EstoqueModel.quantidade_atual.label("quantidade_atual"),
                EstoqueModel.corredor.label("corredor"),
                EstoqueModel.prateleira.label("prateleira"),
                EstoqueModel.secao.label("secao"),
                EstoqueModel.entrada_id.label("entrada_id"),
                LoteModel.id.label("lote_id"),
                LoteModel.numero.label("lote_numero"),
                ProdutoModel.id.label("produto_id"),
                ProdutoModel.nome.label("produto_nome"),
            )
            .join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
            .where(EstoqueModel.id == estoque_id)
        )
        result = await db.execute(query)

        return result.mappings().one_or_none()

    @staticmethod
    async def lock_by_id(db: AsyncSession, estoque_id: int) -> Optional[EstoqueModel]:
        result = await db.execute(select(EstoqueModel).where(EstoqueModel.id == estoque_id).with_for_update())

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def get_context(db: AsyncSession, estoque_id: int):
        query = (
            select(
                EstoqueModel.id.label("estoque_id"),
                EntradaModel.id.label("entrada_id"),
                EntradaModel.data_entrada.label("data_entrada"),
                LoteModel.id.label("lote_id"),
                LoteModel.numero.label("lote_numero"),
                ProdutoModel.id.label("produto_id"),
                ProdutoModel.nome.label("produto_nome"),
                ProdutoModel.preco_venda_atual.label("preco_venda_atual")
            )
            .join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
            .where(EstoqueModel.id == estoque_id)
        )
        result = await db.execute(query)

        return result.mappings().one_or_none()

    @staticmethod
    async def lock_by_entry(db: AsyncSession, entrada_id: int) -> EstoqueModel | None:
        query = select(EstoqueModel).where(EstoqueModel.entrada_id == entrada_id).with_for_update()

        result = await db.execute(query)

        return (
            result
            .scalars()
            .unique()
            .one_or_none()
        )

    @staticmethod
    async def find_by_entry(db: AsyncSession, entrada_id: int) -> Optional[EstoqueModel]:
        result = await db.execute(select(EstoqueModel).where(EstoqueModel.entrada_id == entrada_id))

        return result.scalars().first()

    @staticmethod
    async def list(db: AsyncSession, search: Optional[str], produto_id: Optional[int], lote_id: Optional[int], somente_com_saldo: bool, page: int, per_page: int):
        conditions = []

        if search:
            value = f"%{search.strip()}%"

            conditions.append(
                or_(
                    ProdutoModel.nome.ilike(value),
                    LoteModel.numero.ilike(value),
                    EstoqueModel.corredor.ilike(value),
                    EstoqueModel.prateleira.ilike(value),
                    EstoqueModel.secao.ilike(value),
                )
            )

        if produto_id is not None:
            conditions.append(ProdutoModel.id == produto_id)

        if lote_id is not None:
            conditions.append(LoteModel.id == lote_id)

        if somente_com_saldo:
            conditions.append(EstoqueModel.quantidade_atual > 0)

        count_query = (
            select(func.count(EstoqueModel.id))
            .join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
        )

        query = (
            select(
                EstoqueModel.id.label("id"),
                EstoqueModel.quantidade_atual.label("quantidade_atual"),
                EstoqueModel.corredor.label("corredor"),
                EstoqueModel.prateleira.label("prateleira"),
                EstoqueModel.secao.label("secao"),
                EstoqueModel.entrada_id.label("entrada_id"),
                LoteModel.id.label("lote_id"),
                LoteModel.numero.label("lote_numero"),
                ProdutoModel.id.label("produto_id"),
                ProdutoModel.nome.label("produto_nome"),
            )
            .join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
        )

        if conditions:
            count_query = count_query.where(*conditions)
            query = query.where(*conditions)

        count_result = await db.execute(count_query)
        total = count_result.scalar_one()

        result = await db.execute(
            query.order_by(
                ProdutoModel.nome.asc(),
                LoteModel.numero.asc(),
                EstoqueModel.id.asc(),
            ).offset((page - 1) * per_page).limit(per_page)
        )

        return result.mappings().all(), total

    @staticmethod
    async def list_by_product(db: AsyncSession, produto_id: int):
        query = (
            select(
                EstoqueModel.id.label("id"),
                EstoqueModel.quantidade_atual.label("quantidade_atual"),
                EstoqueModel.corredor.label("corredor"),
                EstoqueModel.prateleira.label("prateleira"),
                EstoqueModel.secao.label("secao"),
                EstoqueModel.entrada_id.label("entrada_id"),
                LoteModel.id.label("lote_id"),
                LoteModel.numero.label("lote_numero"),
                ProdutoModel.id.label("produto_id"),
                ProdutoModel.nome.label("produto_nome"),
            )
            .join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
            .where(ProdutoModel.id == produto_id)
            .order_by(
                LoteModel.numero.asc(),
                EstoqueModel.id.asc(),
            )
        )
        result = await db.execute(query)

        return result.mappings().all()
        
    @staticmethod
    async def update(db: AsyncSession, estoque: EstoqueModel, values: dict) -> EstoqueModel:
        for field, value in values.items():
            setattr(estoque, field, value)

        await db.flush()

        return estoque