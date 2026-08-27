from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import NivelAcessoEnum
from models.usuario_model import UsuarioModel

class UsuarioRepository:
    @staticmethod
    async def find_by_email(db: AsyncSession, email: str) -> Optional[UsuarioModel]:
        query = select(UsuarioModel).filter(UsuarioModel.email == email)
        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def create(db: AsyncSession, nome: str, email: str, hashed_password: str, endereco_id: int, contato_id: int, nivel_acesso: NivelAcessoEnum) -> UsuarioModel:
        usuario = UsuarioModel(
            nome=nome,
            email=email,
            password=hashed_password,
            endereco_id=endereco_id,
            contato_id=contato_id,
            nivel_acesso=nivel_acesso
        )

        db.add(usuario)
        await db.flush()

        return usuario