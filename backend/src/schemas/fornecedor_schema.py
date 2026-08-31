from typing import Optional, List
from pydantic import BaseModel as SCBaseModel, Field

from schemas.contato_schema import ContatoResponseSchema
from schemas.endereco_schema import EnderecoResponseSchema

class FornecedorBaseSchema(SCBaseModel):
    nome: str = Field(min_length=1, max_length=50)
    cnpj: str = Field(min_length=14, max_length=14, pattern=r"^\d{14}$")
    endereco_id: int
    contato_id: int

class FornecedorCreateSchema(FornecedorBaseSchema):
    pass

class FornecedorUpdateSchema(SCBaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=50)
    cnpj: Optional[str] = Field(default=None, min_length=14, max_length=14, pattern=r"^\d{14}$")
    endereco_id: Optional[int] = None
    contato_id: Optional[int] = None

class FornecedorListItemSchema(SCBaseModel):
    id: int
    nome: str
    cnpj: str

    class Config:
        from_attributes = True

class FornecedorDetailSchema(FornecedorListItemSchema):
    endereco_id: int
    contato_id: int

    endereco: EnderecoResponseSchema
    contato: ContatoResponseSchema

class FornecedorListResponseSchema(SCBaseModel):
    items: List[FornecedorListItemSchema]
    total: int
    page: int
    per_page: int