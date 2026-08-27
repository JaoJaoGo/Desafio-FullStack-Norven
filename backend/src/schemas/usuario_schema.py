from typing import Optional
from pydantic import BaseModel as SCBaseModel, EmailStr, Field

from core.enums import NivelAcessoEnum
from schemas.endereco_schema import EnderecoResponseSchema
from schemas.contato_schema import ContatoResponseSchema

class UsuarioBaseSchema(SCBaseModel):
    nome: str
    email: EmailStr
    nivel_acesso: NivelAcessoEnum
    endereco_id: int
    contato_id: int


class UsuarioCreateSchema(SCBaseModel):
    nome: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    endereco: EnderecoResponseSchema
    contato: ContatoResponseSchema


class UsuarioUpdateSchema(SCBaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=72)
    nivel_acesso: Optional[NivelAcessoEnum] = None
    endereco_id: Optional[int] = None
    contato_id: Optional[int] = None


class UsuarioResponseSchema(UsuarioBaseSchema):
    id: int

    class Config:
        from_attributes = True