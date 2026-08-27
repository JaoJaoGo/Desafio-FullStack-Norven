from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.usuario_controller import UsuarioController
from core.deps import get_session

from schemas.usuario_schema import UsuarioCreateSchema, UsuarioResponseSchema

router = APIRouter()

@router.post("/", response_model=UsuarioResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_usuario(data: UsuarioCreateSchema, db: AsyncSession = Depends(get_session)):
    return await UsuarioController.create_usuario(data, db)