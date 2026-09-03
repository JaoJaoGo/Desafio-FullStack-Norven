from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.cidade_model import CidadeModel
from models.estado_model import EstadoModel
from models.pais_model import PaisModel

class GeografiaRepository:
    @staticmethod
    async def list_paises(db: AsyncSession) -> list[PaisModel]:
        query = select(PaisModel).order_by(func.coalesce(PaisModel.nome_pt, PaisModel.nome).asc())
        result = await db.execute(query)

        return list(result.scalars().all())

    @staticmethod
    async def list_estados(db: AsyncSession, pais_id: int) -> list[EstadoModel]:
        query = select(EstadoModel).where(EstadoModel.pais_id == pais_id).order_by(EstadoModel.nome.asc())
        result = await db.execute(query)

        return list(result.scalars().all())
    
    @staticmethod
    async def list_cidades(db: AsyncSession, estado_id: int) -> list[CidadeModel]:
        query = select(CidadeModel).where(CidadeModel.estado_id == estado_id).order_by(CidadeModel.nome.asc())
        result = await db.execute(query)

        return list(result.scalars().all())

    @staticmethod
    async def find_cidade_hierarquia(db: AsyncSession, cidade_id: int) -> Optional[tuple[CidadeModel, EstadoModel, PaisModel]]:
        query = (
            select(CidadeModel, EstadoModel, PaisModel)
            .join(EstadoModel, CidadeModel.estado_id == EstadoModel.id)
            .join(PaisModel, EstadoModel.pais_id == PaisModel.id)
            .where(CidadeModel.id == cidade_id)
        )
        result = await db.execute(query)
        row = result.one_or_none()

        if row is None:
            return None

        return (
            row[0],
            row[1],
            row[2],
        )