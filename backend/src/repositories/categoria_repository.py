from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.categoria_model import CategoriaModel

class CategoriaRepository:
    @staticmethod
    async def find_by_id(db: AsyncSession, categoria_id: int) -> Optional[CategoriaModel]:
        query = select(CategoriaModel).filter(CategoriaModel.id == categoria_id)
        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def find_by_name(db: AsyncSession, nome: str) -> Optional[CategoriaModel]:
        query = select(CategoriaModel).where(CategoriaModel.nome == nome)

        result = await db.execute(query)

        return result.scalars().unique().one_or_none()


    @staticmethod
    async def list(db: AsyncSession, search: Optional[str], page: int, per_page: int) -> tuple[list[CategoriaModel], int]:
        conditions = []

        if search:
            conditions.append(CategoriaModel.nome.ilike(f"%{search.strip()}%"))

        # TOTAL
        count_query = select(func.count(CategoriaModel.id))

        if conditions: count_query = (count_query.where(*conditions))

        count_result = await db.execute(count_query)

        total = count_result.scalar_one()

        # REGISTROS
        query = select(CategoriaModel)

        if conditions: query = query.where(*conditions)

        query = (
            query.order_by(CategoriaModel.nome.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await db.execute(query)

        categorias = list(result.scalars().all())

        return categorias, total


    @staticmethod
    async def create(db: AsyncSession, nome: str) -> CategoriaModel:
        categoria = CategoriaModel(nome=nome)

        db.add(categoria)
        await db.flush()

        return categoria

    @staticmethod
    async def update(db: AsyncSession, categoria: CategoriaModel, values: dict) -> CategoriaModel:
        for field, value in values.items():
            setattr(categoria, field, value)
            
        await db.flush()

        return categoria