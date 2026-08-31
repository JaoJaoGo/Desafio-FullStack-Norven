from sqlalchemy.ext.asyncio import AsyncSession

from models.usuario_model import UsuarioModel
from schemas.entrada_schema import EntradaFilterSchema, EntradaUpdateSchema
from services.entrada_service import EntradaService

class EntradaController:
    @staticmethod
    async def create(db: AsyncSession, produto_id: int, data, current_user: UsuarioModel):
        return await EntradaService.create(db=db, produto_id=produto_id, data=data, current_user=current_user)

    @staticmethod
    async def list(db: AsyncSession, filters: EntradaFilterSchema):
        return await EntradaService.list(db, filters)

    @staticmethod
    async def find_by_id(db: AsyncSession, entrada_id: int):
        return await EntradaService.find_by_id(db, entrada_id)

    @staticmethod
    async def update(db: AsyncSession, entrada_id: int, data: EntradaUpdateSchema):
        return await EntradaService.update(db, entrada_id, data)