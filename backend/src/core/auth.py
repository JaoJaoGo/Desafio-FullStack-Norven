from datetime import datetime, timedelta
from pytz import timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from pydantic import EmailStr

from models.usuario_model import UsuarioModel
from core.configs import settings
from core.security import verify_password

# Endpoint de autenticação
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def authenticate(email: EmailStr, password: str, db: AsyncSession) -> Optional[UsuarioModel]:
    query = select(UsuarioModel).where(UsuarioModel.email == email)
    result = await db.execute(query)
    usuario: UsuarioModel = result.scalars().unique().one_or_none()

    if not usuario:
        return None

    if not verify_password(password, usuario.password):
        return None
        
    return usuario

def _create_token(tipo_token: str, tempo_vida: timedelta, sub: str) -> str:
    payload = {}

    sp = timezone('America/Sao_Paulo')
    expira = datetime.now(sp) + tempo_vida

    payload['type'] = tipo_token
    payload['exp'] = expira
    payload['iat'] = datetime.now(tz=sp)
    payload['sub'] = str(sub)

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

def create_access_token(sub: str) -> str:
    return _create_token(
        tipo_token="access_token",
        tempo_vida=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        sub=sub
    )