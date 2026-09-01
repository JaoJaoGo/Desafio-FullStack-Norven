from typing import Optional, List
from pydantic import BaseModel as SCBaseModel, EmailStr, Field
from pydantic_settings import SettingsConfigDict

from core.enums import NivelAcessoEnum
from schemas.endereco_schema import EnderecoCreateSchema, EnderecoUpdateSchema, EnderecoResponseSchema
from schemas.contato_schema import ContatoCreateSchema, ContatoUpdateSchema, ContatoResponseSchema

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
    nivel_acesso: NivelAcessoEnum
    endereco: EnderecoCreateSchema
    contato: ContatoCreateSchema

class UsuarioUpdateSchema(SCBaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=72)
    nivel_acesso: Optional[NivelAcessoEnum] = None
    endereco: Optional[EnderecoUpdateSchema] = None
    contato: Optional[ContatoUpdateSchema] = None

class UsuarioResponseSchema(UsuarioBaseSchema):
    id: int

    model_config = SettingsConfigDict(
        from_attributes=True
    )

class UsuarioDetailResponseSchema(UsuarioResponseSchema):
    endereco: EnderecoResponseSchema
    contato: ContatoResponseSchema

    model_config = SettingsConfigDict(
        from_attributes=True
    )

class UsuarioListResponseSchema(SCBaseModel):
    items: List[UsuarioResponseSchema]
    total: int
    page: int
    per_page: int