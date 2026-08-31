from sqlalchemy.ext.asyncio import AsyncSession

from models.usuario_model import UsuarioModel
from schemas.saida_schema import SaidaFilterSchema, SaidaUpdateSchema
from services.saida_service import SaidaService

class SaidaController:
    @staticmethod
    async def create(db: AsyncSession, produto_id: int, data, current_user: UsuarioModel):
        return await SaidaService.create(db=db, produto_id=produto_id, data=data, current_user=current_user)

    @staticmethod
    async def list(db: AsyncSession, filters: SaidaFilterSchema):
        return await SaidaService.list(db, filters)

    @staticmethod
    async def find_by_id(db: AsyncSession, saida_id: int):
        return await SaidaService.find_by_id(db, saida_id)

    @staticmethod
    async def update(db: AsyncSession, saida_id: int, data: SaidaUpdateSchema):
        return await SaidaService.update(db, saida_id, data)