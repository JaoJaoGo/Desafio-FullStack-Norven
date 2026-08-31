from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.categoria_controller import CategoriaController
from core.deps import get_current_user, get_session
from schemas.categoria_schema import CategoriaCreateSchema, CategoriaResponseSchema, CategoriaListResponseSchema, CategoriaUpdateSchema

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/", response_model=CategoriaResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_categoria(data: CategoriaCreateSchema, db: AsyncSession = Depends(get_session)):
    return await CategoriaController.create(data=data, db=db)

@router.get("/", response_model=CategoriaListResponseSchema)
async def list_categorias(
    search: Optional[str] = Query(default=None, description="Pesquisa pelo nome"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    items, total = await CategoriaController.list(db=db, search=search, page=page, per_page=per_page)

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/{categoria_id}", response_model=CategoriaResponseSchema)
async def get_categoria(categoria_id: int, db: AsyncSession = Depends(get_session)):
    return await CategoriaController.find_by_id(categoria_id=categoria_id, db=db)

@router.patch("/{categoria_id}", response_model=CategoriaResponseSchema)
async def update_categoria(categoria_id: int, data: CategoriaUpdateSchema, db: AsyncSession = Depends(get_session)):
    return await CategoriaController.update(categoria_id=categoria_id, data=data, db=db)