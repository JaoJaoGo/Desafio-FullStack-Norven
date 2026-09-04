from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.lote_controller import LoteController
from core.deps import get_current_user, get_session
from schemas.lote_schema import LoteCreateSchema, LoteFilterSchema, LoteListResponseSchema, LoteResponseSchema

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

@router.post('/', response_model=LoteResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_lote(data: LoteCreateSchema, db: AsyncSession = Depends(get_session)):
    return await LoteController.create(db, data)

@router.get('/', response_model=LoteListResponseSchema)
async def list_lotes(
    search: Optional[str] = None,
    produto_id: Optional[int] = None,
    validade_inicio: Optional[date] = None,
    validade_fim: Optional[date] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    filters = LoteFilterSchema(
        search=search,
        produto_id=produto_id,
        validade_inicio=validade_inicio,
        validade_fim=validade_fim,
        page=page,
        per_page=per_page
    )
    
    items, total = await LoteController.list(db, filters)

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get('/{lote_id}', response_model=LoteResponseSchema)
async def get_lote(lote_id: int, db: AsyncSession = Depends(get_session)):
    return await LoteController.find_by_id(db, lote_id)