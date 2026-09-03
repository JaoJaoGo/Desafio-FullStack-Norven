from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from models.usuario_model import UsuarioModel
from controllers.usuario_controller import UsuarioController
from core.deps import get_session, get_current_user

from schemas.usuario_schema import UsuarioCreateSchema, UsuarioDetailResponseSchema, UsuarioListResponseSchema, UsuarioResponseSchema, UsuarioUpdateSchema

router = APIRouter()

# =========================================================
# PÚBLICO
# =========================================================

@router.post("/", response_model=UsuarioResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_usuario(data: UsuarioCreateSchema, db: AsyncSession = Depends(get_session)):
    return await UsuarioController.create(data, db)

# =========================================================
# PROTEGIDAS
# =========================================================

@router.get("/", response_model=UsuarioListResponseSchema, dependencies=[Depends(get_current_user)])
async def list_usuarios(
    search: Optional[str] = Query(default=None, description="Busca por nome ou e-mail"),
    nivel_acesso: Optional[str] = Query(default=None, description="Filtra pelo nível de acesso"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    usuarios, total = await UsuarioController.list(db=db, search=search, nivel_acesso=nivel_acesso, page=page, per_page=per_page)

    return {
        "items": usuarios,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/{usuario_id}", response_model=UsuarioDetailResponseSchema, dependencies=[Depends(get_current_user)])
async def get_usuario(usuario_id: int, db: AsyncSession = Depends(get_session)):
    return await UsuarioController.find_by_id(usuario_id=usuario_id, db=db)


@router.patch("/{usuario_id}", response_model=UsuarioDetailResponseSchema)
async def update_usuario(usuario_id: int, data: UsuarioUpdateSchema, db: AsyncSession = Depends(get_session), current_user: UsuarioModel = Depends(get_current_user)):
    return await UsuarioController.update(usuario_id=usuario_id, data=data, db=db, current_user_id=current_user.id)