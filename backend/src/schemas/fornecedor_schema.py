from typing import Optional, List
from pydantic import BaseModel as SCBaseModel, Field, ConfigDict

from schemas.contato_schema import ContatoCreateSchema, ContatoResponseSchema, ContatoUpdateSchema
from schemas.endereco_schema import EnderecoCreateSchema, EnderecoResponseSchema, EnderecoUpdateSchema

class FornecedorBaseSchema(SCBaseModel):
    nome: str = Field(min_length=1, max_length=50)
    cnpj: str = Field(min_length=14, max_length=14, pattern=r"^\d{14}$")
    endereco: EnderecoCreateSchema
    contato: ContatoCreateSchema

class FornecedorCreateSchema(FornecedorBaseSchema):
    pass

class FornecedorUpdateSchema(SCBaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=50)
    cnpj: Optional[str] = Field(default=None, min_length=14, max_length=14, pattern=r"^\d{14}$")
    endereco: Optional[EnderecoUpdateSchema] = None
    contato: Optional[ContatoUpdateSchema] = None

class FornecedorListItemSchema(SCBaseModel):
    id: int
    nome: str
    cnpj: str

    model_config = ConfigDict(
        from_attributes=True
    )

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