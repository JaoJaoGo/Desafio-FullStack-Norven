from sqlalchemy.ext.asyncio import AsyncSession

from models.endereco_model import EnderecoModel
from schemas.endereco_schema import EnderecoCreateSchema, EnderecoUpdateSchema

class EnderecoRepository:
    @staticmethod
    async def create(db: AsyncSession, data: EnderecoCreateSchema) -> EnderecoModel:
        endereco = EnderecoModel(**data.model_dump())

        db.add(endereco)
        await db.flush()

        return endereco

    @staticmethod
    async def update(db: AsyncSession, endereco: EnderecoModel, data: EnderecoUpdateSchema) -> EnderecoModel:
        for key, value in data.model_dump().items():
            setattr(endereco, key, value)
        
        await db.flush()
        
        return endereco