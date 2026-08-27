from decimal import Decimal
from typing import Optional
from pydantic import BaseModel as SCBaseModel, Field

class EstoqueBaseSchema(SCBaseModel):
    quantidade_atual: Decimal = Field(ge=0, max_digits=12, decimal_places=3)
    corredor: str = Field(min_length=1, max_length=30)
    prateleira: str = Field(min_length=1, max_length=30)
    secao: str = Field(min_length=1, max_length=30)
    entrada_id: int

class EstoqueCreateSchema(EstoqueBaseSchema):
    pass

class EstoqueUpdateSchema(SCBaseModel):
    quantidade_atual: Optional[Decimal] = Field(default=None, ge=0, max_digits=12, decimal_places=3)
    corredor: Optional[str] = Field(default=None, min_length=1, max_length=30)
    prateleira: Optional[str] = Field(default=None, min_length=1, max_length=30)
    secao: Optional[str] = Field(default=None, min_length=1, max_length=30)
    entrada_id: Optional[int] = None

class EstoqueResponseSchema(EstoqueBaseSchema):
    id: int

    class Config:
        from_attributes = True