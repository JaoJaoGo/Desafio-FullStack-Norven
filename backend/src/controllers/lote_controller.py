from sqlalchemy.ext.asyncio import AsyncSession

from schemas.lote_schema import LoteCreateSchema, LoteFilterSchema, LoteUpdateSchema
from services.lote_service import LoteService

class LoteController:
    @staticmethod
    async def create(db: AsyncSession, data: LoteCreateSchema):
        return await LoteService.create(db, data)

    @staticmethod
    async def list(db: AsyncSession, filters: LoteFilterSchema):
        return await LoteService.list(db, filters)

    @staticmethod
    async def find_by_id(db: AsyncSession, lote_id: int):
        return await LoteService.find_by_id(db, lote_id)

    @staticmethod
    async def update(db: AsyncSession, lote_id: int, data: LoteUpdateSchema):
        return await LoteService.update(db, lote_id, data)