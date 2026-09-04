from datetime import datetime
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.saida_controller import SaidaController
from core.deps import get_current_user, get_session
from core.enums import TipoSaidaEnum
from models.usuario_model import UsuarioModel
from schemas.saida_schema import SaidaCreateSchema, SaidaFilterSchema, SaidaListResponseSchema, SaidaResponseSchema

router = APIRouter()

@router.post("/", response_model=SaidaResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_saida(data: SaidaCreateSchema, db: AsyncSession = Depends(get_session), current_user: UsuarioModel = Depends(get_current_user)):
    return await SaidaController.create(db, data.produto_id, data, current_user)

@router.get("/", response_model=SaidaListResponseSchema, dependencies=[Depends(get_current_user)])
async def list_saidas(
    search: Optional[str] = None,
    produto_id: Optional[int] = Query(default=None, ge=1),
    usuario_id: Optional[int] = Query(default=None, ge=1),
    tipo_saida: Optional[TipoSaidaEnum] = None,
    quantidade_min: Optional[Decimal] = Query(default=None, ge=0),
    quantidade_max: Optional[Decimal] = Query(default=None, ge=0),
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    filters = SaidaFilterSchema(
        search=search,
        produto_id=produto_id,
        usuario_id=usuario_id,
        tipo_saida=tipo_saida,
        quantidade_min=quantidade_min,
        quantidade_max=quantidade_max,
        data_inicio=data_inicio,
        data_fim=data_fim,
        page=page,
        per_page=per_page
    )

    items, total = await SaidaController.list(db, filters)

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/{saida_id}", response_model=SaidaResponseSchema, dependencies=[Depends(get_current_user)])
async def get_saida(saida_id: int, db: AsyncSession = Depends(get_session)):
    return await SaidaController.find_by_id(db, saida_id)