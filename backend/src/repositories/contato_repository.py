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
    async def update(db: AsyncSession, contato: ContatoModel, data: ContatoUpdateSchema) -> ContatoModel:
        for key, value in data.model_dump().items():
            setattr(contato, key, value)
        
        await db.flush()
        
        return contato