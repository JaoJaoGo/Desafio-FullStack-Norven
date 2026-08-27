from typing import Optional
from pydantic import BaseModel as SCBaseModel, EmailStr

from core.enums import NivelAcessoEnum

class UsuarioBaseSchema(SCBaseModel):
    nome: str
    email: EmailStr
    nivel_acesso: NivelAcessoEnum
    endereco_id: int
    contato_id: int


class UsuarioCreateSchema(UsuarioBaseSchema):
    password: str


class UsuarioUpdateSchema(SCBaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    nivel_acesso: Optional[NivelAcessoEnum] = None
    endereco_id: Optional[int] = None
    contato_id: Optional[int] = None


class UsuarioResponseSchema(UsuarioBaseSchema):
    id: int

    class Config:
        from_attributes = True