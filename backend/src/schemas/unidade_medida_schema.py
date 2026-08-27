from typing import Optional
from pydantic import BaseModel as SCBaseModel, Field


class UnidadeMedidaBaseSchema(SCBaseModel):
    nome: str = Field(min_length=1, max_length=30)
    sigla: str = Field(min_length=1, max_length=5)


class UnidadeMedidaCreateSchema(UnidadeMedidaBaseSchema):
    pass


class UnidadeMedidaUpdateSchema(SCBaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=30)
    sigla: Optional[str] = Field(default=None, min_length=1, max_length=5)


class UnidadeMedidaResponseSchema(UnidadeMedidaBaseSchema):
    id: int

    class Config:
        from_attributes = True