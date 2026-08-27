from datetime import date
from typing import Optional
from pydantic import BaseModel as SCBaseModel, Field

class LoteBaseSchema(SCBaseModel):
    numero: str = Field(min_length=1, max_length=30)
    data_validade: date
    produto_id: int

class LoteCreateSchema(LoteBaseSchema):
    pass

class LoteUpdateSchema(SCBaseModel):
    numero: Optional[str] = Field(default=None, min_length=1, max_length=30)
    data_validade: Optional[date] = None
    produto_id: Optional[int] = None

class LoteResponseSchema(LoteBaseSchema):
    id: int

    class Config:
        from_attributes = True