from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.fornecedor_schema import FornecedorCreateSchema, FornecedorUpdateSchema
from services.fornecedor_service import FornecedorService

class FornecedorController:
    @staticmethod
    async def create(db: AsyncSession, data: FornecedorCreateSchema):
        return await FornecedorService.create(db, data)

    @staticmethod
    async def list(db: AsyncSession, search: Optional[str], page: int, per_page: int):
        return await FornecedorService.list(db, search, page, per_page)

    @staticmethod
    async def find_by_id(db: AsyncSession, fornecedor_id: int):
        return await FornecedorService.find_by_id(db, fornecedor_id)

    @staticmethod
    async def update(db: AsyncSession, fornecedor_id: int, data: FornecedorUpdateSchema):
        return await FornecedorService.update(db, fornecedor_id, data)