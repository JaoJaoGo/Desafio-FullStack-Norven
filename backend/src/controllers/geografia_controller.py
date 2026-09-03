from sqlalchemy.ext.asyncio import AsyncSession

from services.geografia_service import GeografiaService

class GeografiaController:
    @staticmethod
    async def list_paises(db: AsyncSession):
        return await GeografiaService.list_paises(db)

    @staticmethod
    async def list_estados(db: AsyncSession, pais_id: int):
        return await GeografiaService.list_estados(db, pais_id)

    @staticmethod
    async def list_cidades(db: AsyncSession, estado_id: int):
        return await GeografiaService.list_cidades(db, estado_id)

    @staticmethod
    async def find_cidade_hierarquia(db: AsyncSession, cidade_id: int):
        return await GeografiaService.find_cidade_hierarquia(db, cidade_id)