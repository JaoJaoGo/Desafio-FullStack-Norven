from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.contato_model import ContatoModel
from schemas.contato_schema import ContatoCreateSchema, ContatoUpdateSchema

class ContatoRepository:
    @staticmethod
    async def create(db: AsyncSession, data: ContatoCreateSchema) -> ContatoModel:
        contato = ContatoModel(**data.model_dump())
        
        db.add(contato)
        await db.flush()
        
        return contato

    @staticmethod
    async def find_by_id(db: AsyncSession, contato_id: int) -> Optional[ContatoModel]:
        query = select(ContatoModel).filter(ContatoModel.id == contato_id)
        result = await db.execute(query)

        return result.scalars().unique().one_or_none()
    
    @staticmethod
    async def find_by_data(db: AsyncSession, data: ContatoCreateSchema) -> Optional[ContatoModel]:
        query = select(ContatoModel).where(
            ContatoModel.cod_pais == data.cod_pais,
            ContatoModel.ddd == data.ddd,
            ContatoModel.numero == data.numero
        )
        result = await db.execute(query)

        return result.scalars().unique().one_or_none()