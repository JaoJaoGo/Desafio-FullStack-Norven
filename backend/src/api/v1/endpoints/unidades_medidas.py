from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.unidade_medida_controller import UnidadeMedidaController
from core.deps import get_current_user, get_session
from schemas.unidade_medida_schema import UnidadeMedidaCreateSchema, UnidadeMedidaListResponseSchema, UnidadeMedidaResponseSchema, UnidadeMedidaUpdateSchema

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/", response_model=UnidadeMedidaResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_unidade_medida(data: UnidadeMedidaCreateSchema, db: AsyncSession = Depends(get_session)):
    return await UnidadeMedidaController.create(data=data, db=db)

@router.get("/", response_model=UnidadeMedidaListResponseSchema)
async def list_unidades_medidas(
    search: Optional[str] = Query(default=None, description="Pesquisa por nome ou sigla"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    items, total = await UnidadeMedidaController.list(db=db, search=search, page=page, per_page=per_page)

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/{unidade_id}", response_model=UnidadeMedidaResponseSchema)
async def get_unidade_medida(unidade_id: int, db: AsyncSession = Depends(get_session)):
    return (await UnidadeMedidaController.find_by_id(unidade_id=unidade_id, db=db))

@router.patch("/{unidade_id}", response_model=UnidadeMedidaResponseSchema)
async def update_unidade_medida(unidade_id: int, data: UnidadeMedidaUpdateSchema, db: AsyncSession = Depends(get_session)):
    return await UnidadeMedidaController.update(unidade_id=unidade_id, data=data, db=db)