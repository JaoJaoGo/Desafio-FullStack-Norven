from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import authenticate, create_access_token
from core.deps import get_session, get_current_user
from models.usuario_model import UsuarioModel
from schemas.auth_schema import TokenResponseSchema
from schemas.usuario_schema import UsuarioResponseSchema

router = APIRouter()

@router.post("/login", response_model=TokenResponseSchema, status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    usuario = await authenticate(email=form_data.username, password=form_data.password, db=db)

    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos.", headers={"WWW-Authenticate": "Bearer"})

    access_token = create_access_token(sub=str(usuario.id))

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get('/me', response_model=UsuarioResponseSchema)
async def me(current_user: UsuarioModel = Depends(get_current_user)):
    return current_user