from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from core.database import Session
from core.auth import oauth2_scheme
from core.configs import settings
from models.usuario_model import UsuarioModel

class TokenData(BaseModel):
    username: Optional[str] = None

async def get_session() -> Generator:
    session: AsyncSession = Session()

    try:
        yield session
    finally:
        await session.close()

async def get_current_user(db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)) -> UsuarioModel:
    credentials_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível autenticar a credencial",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False}
        )

        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception

        token_data = TokenData(username=str(subject))

        try:
            usuario_id = int(token_data.username)
        except (TypeError, ValueError):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    query = select(UsuarioModel).where(UsuarioModel.id == usuario_id)
    result = await db.execute(query)

    user = result.scalars().unique().one_or_none()

    if user is None:
        raise credentials_exception

    return user