from typing import Optional
from sqlalchemy import String, cast, select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.enums import NivelAcessoEnum
from models.usuario_model import UsuarioModel

class UsuarioRepository:
    @staticmethod
    async def find_by_email(db: AsyncSession, email: str) -> Optional[UsuarioModel]:
        query = select(UsuarioModel).filter(UsuarioModel.email == email)
        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def find_by_id(db: AsyncSession, usuario_id: int, with_relations: bool = False) -> Optional[UsuarioModel]:
        query = select(UsuarioModel).where(UsuarioModel.id == usuario_id)

        if with_relations:
            query = (
                query
                .options(
                    selectinload(UsuarioModel.endereco),
                    selectinload(UsuarioModel.contato)
                )
                .execution_options(populate_existing=True)
            )

        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def list(db: AsyncSession, search: Optional[str], nivel_acesso: Optional[str], page: int, per_page: int) -> tuple[list[UsuarioModel], int]:
        filters = []

        if search:
            search_value = f"%{search.strip()}%"

            filters.append(
                or_(
                    UsuarioModel.nome.ilike(search_value),
                    UsuarioModel.email.ilike(search_value)
                )
            )

        if nivel_acesso:
            filters.append(
                func.lower(
                    cast(
                        UsuarioModel.nivel_acesso,
                        String,
                    )
                )
                == nivel_acesso.strip().lower()
            )

        count_query = select(func.count(UsuarioModel.id))

        query = select(UsuarioModel)

        if filters:
            count_query = count_query.where(*filters)
            query = query.where(*filters)

        count_result = await db.execute(count_query)

        total = count_result.scalar_one()

        offset = (page - 1) * per_page

        query = (
            query
            .order_by(UsuarioModel.nome.asc())
            .offset(offset)
            .limit(per_page)
        )

        result = await db.execute(query)

        usuarios = list(result.scalars().all())

        return usuarios, total

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

    @staticmethod
    async def update(db: AsyncSession, usuario: UsuarioModel, values: dict) -> UsuarioModel:
        for field, value in values.items():
            setattr(usuario, field, value)

        await db.flush()

        return usuario