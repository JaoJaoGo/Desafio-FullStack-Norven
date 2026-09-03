from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from models.usuario_model import UsuarioModel
from schemas.usuario_schema import UsuarioCreateSchema, UsuarioUpdateSchema
from services.usuario_service import UsuarioService

class UsuarioController:
    @staticmethod
    async def create(data: UsuarioCreateSchema, db: AsyncSession) -> UsuarioModel:
        return await UsuarioService.create_usuario(db, data)

    @staticmethod
    async def list(db: AsyncSession, search: Optional[str], nivel_acesso: Optional[str], page: int, per_page: int) -> tuple[list[UsuarioModel], int]:
        return await UsuarioService.list(db, search, nivel_acesso, page, per_page)

    @staticmethod
    async def find_by_id(usuario_id: int, db: AsyncSession) -> UsuarioModel:
        return await UsuarioService.find_by_id(db, usuario_id)

    @staticmethod
    async def update(usuario_id: int, data: UsuarioUpdateSchema, db: AsyncSession, current_user_id: int) -> UsuarioModel:
        return await UsuarioService.update(db=db, usuario_id=usuario_id, data=data, current_user_id=current_user_id)