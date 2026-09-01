from typing import Optional
from pydantic import BaseModel as SCBaseModel, Field
from pydantic_settings import SettingsConfigDict

class EnderecoBaseSchema(SCBaseModel):
    logradouro: str = Field(min_length=1, max_length=100)
    numero: str = Field(min_length=1, max_length=10)
    complemento: Optional[str] = Field(default=None, max_length=50)
    cep: str = Field(min_length=9, max_length=9)
    bairro: str = Field(min_length=1, max_length=50)
    municipio_id: int = Field(gt=0)

class EnderecoCreateSchema(EnderecoBaseSchema):
    pass

class EnderecoUpdateSchema(SCBaseModel):
    logradouro: Optional[str] = Field(default=None, min_length=1, max_length=100)
    numero: Optional[str] = Field(default=None, min_length=1, max_length=10)
    complemento: Optional[str] = Field(default=None, max_length=50)
    cep: Optional[str] = Field(default=None, min_length=9, max_length=9)
    bairro: Optional[str] = Field(default=None, min_length=1, max_length=50)
    municipio_id: Optional[int] = Field(default=None, gt=0)

class EnderecoResponseSchema(EnderecoBaseSchema):
    id: int

    model_config = SettingsConfigDict(
        from_attributes=True
    )