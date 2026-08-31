from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.fornecedor_controller import FornecedorController
from core.deps import get_current_user, get_session
from schemas.fornecedor_schema import FornecedorCreateSchema, FornecedorDetailSchema, FornecedorListResponseSchema, FornecedorUpdateSchema

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

@router.post('/', response_model=FornecedorDetailSchema, status_code=status.HTTP_201_CREATED)
async def create_fornecedor(data: FornecedorCreateSchema, db: AsyncSession = Depends(get_session)):
    return await FornecedorController.create(db, data)

@router.get('/', response_model=FornecedorListResponseSchema)
async def list_fornecedores(
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    items, total = await FornecedorController.list(db, search, page, per_page)

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get('/{fornecedor_id}', response_model=FornecedorDetailSchema)
async def get_fornecedor(fornecedor_id: int, db: AsyncSession = Depends(get_session)):
    return await FornecedorController.find_by_id(db, fornecedor_id)

@router.patch("/{fornecedor_id}", response_model=FornecedorDetailSchema)
async def update_fornecedor(fornecedor_id: int, data: FornecedorUpdateSchema, db: AsyncSession = Depends(get_session)):
    return await FornecedorController.update(db, fornecedor_id, data)