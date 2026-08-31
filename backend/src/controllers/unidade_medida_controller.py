from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.unidade_medida_schema import UnidadeMedidaCreateSchema, UnidadeMedidaUpdateSchema
from services.unidade_medida_service import UnidadeMedidaService

class UnidadeMedidaController:
    @staticmethod
    async def create(data: UnidadeMedidaCreateSchema, db: AsyncSession):
        return await UnidadeMedidaService.create(db, data)

    @staticmethod
    async def list(db: AsyncSession, search: Optional[str], page: int, per_page: int):
        return await UnidadeMedidaService.list(db=db, search=search, page=page, per_page=per_page)

    @staticmethod
    async def find_by_id(unidade_id: int, db: AsyncSession):
        return await UnidadeMedidaService.find_by_id(db, unidade_id)

    @staticmethod
    async def update(unidade_id: int, data: UnidadeMedidaUpdateSchema, db: AsyncSession):
        return await UnidadeMedidaService.update(db=db, unidade_id=unidade_id, data=data)