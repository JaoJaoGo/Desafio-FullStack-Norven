from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.geografia_controller import GeografiaController
from core.deps import get_current_user, get_session
from schemas.geografia_schema import CidadeHierarquiaResponseSchema, CidadeResponseSchema, EstadoResponseSchema, PaisResponseSchema

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

@router.get('/paises', response_model=list[PaisResponseSchema])
async def list_paises(db: AsyncSession = Depends(get_session)):
    return await GeografiaController.list_paises(db)

@router.get('/estados', response_model=list[EstadoResponseSchema])
async def list_estados(pais_id: int = Query(gt=0), db: AsyncSession = Depends(get_session)):
    return await GeografiaController.list_estados(db, pais_id)

@router.get('/cidades', response_model=list[CidadeResponseSchema])
async def list_cidades(estado_id: int = Query(gt=0), db: AsyncSession = Depends(get_session)):
    return await GeografiaController.list_cidades(db, estado_id)

@router.get('/cidades/{cidade_id}/hierarquia', response_model=CidadeHierarquiaResponseSchema)
async def get_cidade_hierarquia(cidade_id: int, db: AsyncSession = Depends(get_session)):
    return await GeografiaController.find_cidade_hierarquia(db, cidade_id)