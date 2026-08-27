from typing import Optional
from pydantic import BaseModel as SCBaseModel

class EnderecoBaseSchema(SCBaseModel):
    logradouro: str
    numero: Optional[str] = None
    complemento: Optional[str] = None
    cep: str
    bairro: str
    municipio_id: int

class EnderecoCreateSchema(EnderecoBaseSchema):
    pass

class EnderecoUpdateSchema(SCBaseModel):
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    cep: Optional[str] = None
    bairro: Optional[str] = None
    municipio_id: Optional[int] = None

class EnderecoResponseSchema(EnderecoBaseSchema):
    id: int

    class Config:
        from_attributes = True