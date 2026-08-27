from typing import Optional
from pydantic import BaseModel as SCBaseModel, Field

class CategoriaBaseSchema(SCBaseModel):
    nome: str = Field(min_length=1, max_length=30)


class CategoriaCreateSchema(CategoriaBaseSchema):
    pass


class CategoriaUpdateSchema(SCBaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=30)


class CategoriaResponseSchema(CategoriaBaseSchema):
    id: int

    class Config:
        from_attributes = True