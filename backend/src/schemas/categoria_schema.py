from typing import Optional, List
from pydantic import BaseModel as SCBaseModel, Field
from pydantic_settings import SettingsConfigDict

class CategoriaBaseSchema(SCBaseModel):
    nome: str = Field(min_length=1, max_length=30)

class CategoriaCreateSchema(CategoriaBaseSchema):
    pass

class CategoriaUpdateSchema(SCBaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=30)

class CategoriaResponseSchema(CategoriaBaseSchema):
    id: int
    nome: str

    model_config = SettingsConfigDict(
        from_attributes=True
    )

class CategoriaListResponseSchema(SCBaseModel):
    items: List[CategoriaResponseSchema]
    total: int
    page: int
    per_page: int