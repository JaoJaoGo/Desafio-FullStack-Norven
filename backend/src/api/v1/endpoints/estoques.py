from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.estoque_controller import EstoqueController
from core.deps import get_current_user, get_session
from schemas.estoque_schema import EstoqueFilterSchema, EstoqueListResponseSchema, EstoqueResponseSchema, EstoqueUpdateSchema

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

@router.get('/', response_model=EstoqueListResponseSchema)
async def list_estoques(
    search: Optional[str] = None,
    produto_id: Optional[int] = Query(default=None, ge=1),
    lote_id: Optional[int] = Query(default=None, ge=1),
    somente_com_saldo: bool = False,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    filters = EstoqueFilterSchema(
        search=search,
        produto_id=produto_id,
        lote_id=lote_id,
        somente_com_saldo=somente_com_saldo,
        page=page,
        per_page=per_page
    )

    items, total = await EstoqueController.list(db, filters)

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get('/{estoque_id}', response_model=EstoqueResponseSchema)
async def get_estoque(estoque_id: int, db: AsyncSession = Depends(get_session)):
    return await EstoqueController.find_by_id(db, estoque_id)

@router.patch('/{estoque_id}', response_model=EstoqueResponseSchema)
async def update_estoque(estoque_id: int, data: EstoqueUpdateSchema, db: AsyncSession = Depends(get_session)):
    return await EstoqueController.update(db, estoque_id, data)