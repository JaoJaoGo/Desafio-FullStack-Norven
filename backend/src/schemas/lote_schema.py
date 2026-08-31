from datetime import date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel as SCBaseModel, Field, model_validator

class LoteBaseSchema(SCBaseModel):
    numero: str = Field(min_length=1, max_length=30)
    data_validade: Optional[date] = None
    produto_id: int = Field(gt=0)

class LoteInlineCreateSchema(SCBaseModel):
    numero: str = Field(min_length=1, max_length=30)
    data_validade: Optional[date] = None

class LoteCreateSchema(LoteBaseSchema):
    pass

class LoteUpdateSchema(SCBaseModel):
    numero: Optional[str] = Field(default=None, min_length=1, max_length=30)

class LoteResponseSchema(SCBaseModel):
    id: int
    numero: str
    data_validade: Optional[date]

    produto_id: int
    produto_nome: str

    estoque_total: Decimal

class LoteListResponseSchema(SCBaseModel):
    items: List[LoteResponseSchema]
    total: int
    page: int
    per_page: int

class LoteFilterSchema(SCBaseModel):
    search: Optional[str] = None
    produto_id: Optional[int] = Field(default=None, gt=0)
    validade_inicio: Optional[date] = None
    validade_fim: Optional[date] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def validar_periodo(self):
        if (
            self.validade_inicio is not None
            and self.validade_fim is not None
            and self.validade_inicio > self.validade_fim
        ):
            raise ValueError("validade_inicio não pode ser maior que validade_fim.")

        return self