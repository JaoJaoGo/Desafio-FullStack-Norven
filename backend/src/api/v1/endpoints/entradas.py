from datetime import datetime
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.entrada_controller import EntradaController
from core.deps import get_current_user, get_session
from models.usuario_model import UsuarioModel
from schemas.entrada_schema import EntradaCreateSchema, EntradaFilterSchema, EntradaListResponseSchema, EntradaResponseSchema


router = APIRouter()

@router.post('/', response_model=EntradaResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_entrada(data: EntradaCreateSchema, db: AsyncSession = Depends(get_session), current_user: UsuarioModel = Depends(get_current_user)):
    return await EntradaController.create(db, data.produto_id, data, current_user)

@router.get('/', response_model=EntradaListResponseSchema, dependencies=[Depends(get_current_user)])
async def list_entradas(
    search: Optional[str] = None,
    produto_id: Optional[int] = Query(default=None, ge=1),
    fornecedor_id: Optional[int] = Query(default=None, ge=1),
    usuario_id: Optional[int] = Query(default=None, ge=1),
    tipo_entrada: Optional[str] = None,
    quantidade_min: Optional[Decimal] = Query(default=None, ge=0),
    quantidade_max: Optional[Decimal] = Query(default=None, ge=0),
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    filters = EntradaFilterSchema(
        search=search,
        produto_id=produto_id,
        fornecedor_id=fornecedor_id,
        usuario_id=usuario_id,
        tipo_entrada=tipo_entrada,
        quantidade_min=quantidade_min,
        quantidade_max=quantidade_max,
        data_inicio=data_inicio,
        data_fim=data_fim,
        page=page,
        per_page=per_page
    )

    items, total = await EntradaController.list(db, filters)

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get('/{entrada_id}', response_model=EntradaResponseSchema, dependencies=[Depends(get_current_user)])
async def get_entrada(entrada_id: int, db: AsyncSession = Depends(get_session)):
    return await EntradaController.find_by_id(db, entrada_id)