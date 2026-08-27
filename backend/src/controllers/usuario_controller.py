from sqlalchemy.ext.asyncio import AsyncSession

from models.usuario_model import UsuarioModel
from schemas.usuario_schema import UsuarioCreateSchema
from services.usuario_service import UsuarioService

class UsuarioController:
    @staticmethod
    async def create(data: UsuarioCreateSchema, db: AsyncSession) -> UsuarioModel:
        return await UsuarioService.create_usuario(db, data)