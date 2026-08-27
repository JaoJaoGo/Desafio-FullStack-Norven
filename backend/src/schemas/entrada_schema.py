from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel as SCBaseModel, Field


class EntradaBaseSchema(SCBaseModel):
    quantidade: Decimal = Field(gt=0, max_digits=12, decimal_places=3)
    preco_custo_unitario: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    fornecedor_id: int
    lote_id: int

class EntradaCreateSchema(EntradaBaseSchema):
    pass

class EntradaUpdateSchema(SCBaseModel):
    data_entrada: Optional[datetime] = None
    quantidade: Optional[Decimal] = Field(default=None, gt=0, max_digits=12, decimal_places=3)
    preco_custo_unitario: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    fornecedor_id: Optional[int] = None
    lote_id: Optional[int] = None

class EntradaResponseSchema(EntradaBaseSchema):
    id: int
    data_entrada: datetime

    class Config:
        from_attributes = True