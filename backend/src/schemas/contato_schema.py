from typing import Optional
from pydantic import BaseModel as SCBaseModel, Field
from pydantic_settings import SettingsConfigDict

class ContatoBaseSchema(SCBaseModel):
    cod_pais: str = Field(min_length=1, max_length=5)
    ddd: str = Field(min_length=2, max_length=3)
    numero: str = Field(min_length=8, max_length=15)

class ContatoCreateSchema(ContatoBaseSchema):
    pass

class ContatoUpdateSchema(SCBaseModel):
    cod_pais: Optional[str] = Field(default=None, min_length=1, max_length=5)
    ddd: Optional[str] = Field(default=None, min_length=2, max_length=3)
    numero: Optional[str] = Field(default=None, min_length=8, max_length=15)

class ContatoResponseSchema(ContatoBaseSchema):
    id: int

    model_config = SettingsConfigDict(
        from_attributes=True
    )