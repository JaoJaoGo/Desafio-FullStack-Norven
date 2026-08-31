from typing import Optional
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.fornecedor_model import FornecedorModel

class FornecedorRepository:
    @staticmethod
    async def find_by_id(db: AsyncSession, fornecedor_id: int, with_relations: bool = False) -> Optional[FornecedorModel]:
        query = select(FornecedorModel).where(FornecedorModel.id == fornecedor_id)

        if with_relations:
            query = query.options(selectinload(FornecedorModel.endereco), selectinload(FornecedorModel.contato))

        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def find_by_cnpj(db: AsyncSession, cnpj: str) -> Optional[FornecedorModel]:
        result = await db.execute(select(FornecedorModel).where(FornecedorModel.cnpj == cnpj))

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def list(db: AsyncSession, search: Optional[str], page: int, per_page: int) -> tuple[list[FornecedorModel], int]:
        conditions = []

        if search:
            value = f"%{search.strip()}%"

            conditions.append(
                or_(
                    FornecedorModel.nome.ilike(value),
                    FornecedorModel.cnpj.ilike(value)
                )
            )

        count_query = select(func.count(FornecedorModel.id))
        query = select(FornecedorModel)

        if conditions:
            count_query = count_query.where(*conditions)
            query = query.where(*conditions)

        total = (await db.execute(count_query)).scalar_one()
        result = await db.execute(query.order_by(FornecedorModel.nome.asc()).offset((page - 1) * per_page).limit(per_page))

        return list(result.scalars().all()), total

    @staticmethod
    async def create(db: AsyncSession, *, nome: str, cnpj: str, endereco_id: int, contato_id: int) -> FornecedorModel:
        fornecedor = FornecedorModel(nome=nome, cnpj=cnpj, endereco_id=endereco_id, contato_id=contato_id)
        
        db.add(fornecedor)
        await db.flush()
        
        return fornecedor

    @staticmethod
    async def update(db: AsyncSession, fornecedor: FornecedorModel, values: dict):
        for field, value in values.items():
            setattr(fornecedor, field, value)

        await db.flush()

        return fornecedor