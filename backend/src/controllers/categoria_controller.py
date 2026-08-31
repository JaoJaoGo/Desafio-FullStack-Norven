from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.categoria_schema import CategoriaCreateSchema, CategoriaUpdateSchema
from services.categoria_service import CategoriaService

class CategoriaController:
    @staticmethod
    async def create(db: AsyncSession, data: CategoriaCreateSchema):
        return await CategoriaService.create(db, data)

    @staticmethod
    async def list(db: AsyncSession, search: Optional[str], page: int, per_page: int):
        return await CategoriaService.list(db=db, search=search, page=page, per_page=per_page)

    @staticmethod
    async def find_by_id(db: AsyncSession, categoria_id: int):
        return await CategoriaService.find_by_id(db, categoria_id)

    @staticmethod
    async def update(db: AsyncSession, data: CategoriaUpdateSchema, categoria_id: int):
        return await CategoriaService.update(db, categoria_id, data)