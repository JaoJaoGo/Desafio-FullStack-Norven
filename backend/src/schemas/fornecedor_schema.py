from typing import Optional
from pydantic import BaseModel as SCBaseModel, Field

class FornecedorBaseSchema(SCBaseModel):
    nome: str
    cnpj: str = Field(min_length=14, max_length=14)
    endereco_id: int
    contato_id: int

class FornecedorCreateSchema(FornecedorBaseSchema):
    pass

class FornecedorUpdateSchema(SCBaseModel):
    nome: Optional[str] = None
    cnpj: Optional[str] = Field(default=None, min_length=14, max_length=14)
    endereco_id: Optional[int] = None
    contato_id: Optional[int] = None

class FornecedorResponseSchema(FornecedorBaseSchema):
    id: int

    class Config:
        from_attributes = True