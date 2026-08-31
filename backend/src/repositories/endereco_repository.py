from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.endereco_model import EnderecoModel
from schemas.endereco_schema import EnderecoCreateSchema


class EnderecoRepository:
    @staticmethod
    async def create(db: AsyncSession, data: EnderecoCreateSchema) -> EnderecoModel:
        endereco = EnderecoModel(**data.model_dump())

        db.add(endereco)
        await db.flush()

        return endereco

    @staticmethod
    async def find_by_id(db: AsyncSession, endereco_id: int) -> Optional[EnderecoModel]:
        query = select(EnderecoModel).where(EnderecoModel.id == endereco_id)
        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def find_by_data(db: AsyncSession, data: EnderecoCreateSchema) -> Optional[EnderecoModel]:
        query = select(EnderecoModel).where(
            EnderecoModel.logradouro == data.logradouro,
            EnderecoModel.numero == data.numero,
            EnderecoModel.complemento == data.complemento,
            EnderecoModel.cep == data.cep,
            EnderecoModel.bairro == data.bairro,
            EnderecoModel.municipio_id == data.municipio_id
        )
        result = await db.execute(query)

        return result.scalars().unique().one_or_none()