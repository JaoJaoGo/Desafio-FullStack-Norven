from sqlalchemy.ext.asyncio import AsyncSession

from schemas.estoque_schema import EstoqueFilterSchema, EstoqueUpdateSchema
from services.estoque_service import EstoqueService

class EstoqueController:
    @staticmethod
    async def list(db: AsyncSession, filters: EstoqueFilterSchema):
        return await EstoqueService.list(db, filters)

    @staticmethod
    async def find_by_id(db: AsyncSession, estoque_id: int):
        return await EstoqueService.find_by_id(db, estoque_id)

    @staticmethod
    async def update(db: AsyncSession, estoque_id: int, data: EstoqueUpdateSchema):
        return await EstoqueService.update(db, estoque_id, data)