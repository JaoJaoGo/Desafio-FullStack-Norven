from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.geografia_repository import GeografiaRepository

class GeografiaService:
    @staticmethod
    async def list_paises(db: AsyncSession):
        return await GeografiaRepository.list_paises(db)

    @staticmethod
    async def list_estados(db: AsyncSession, pais_id: int):
        return await GeografiaRepository.list_estados(db, pais_id)

    @staticmethod
    async def list_cidades(db: AsyncSession, estado_id: int):
        return await GeografiaRepository.list_cidades(db, estado_id)

    @staticmethod
    async def find_cidade_hierarquia(db: AsyncSession, cidade_id: int):
        hierarquia = await GeografiaRepository.find_cidade_hierarquia(db, cidade_id)

        if hierarquia is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cidade ou hierarquia geográfica não encontrada.")

        cidade, estado, pais = hierarquia
        
        return {
            "cidade": cidade,
            "estado": estado,
            "pais": pais,
        }