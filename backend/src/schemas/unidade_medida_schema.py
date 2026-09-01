from typing import Optional, List
from pydantic import BaseModel as SCBaseModel, Field
from pydantic_settings import SettingsConfigDict

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
    nome: str
    sigla: str

    model_config = SettingsConfigDict(
        from_attributes=True
    )

class UnidadeMedidaListResponseSchema(SCBaseModel):
    items: List[UnidadeMedidaResponseSchema]
    total: int
    page: int
    per_page: int