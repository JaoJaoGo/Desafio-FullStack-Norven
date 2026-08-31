from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel as SCBaseModel, Field, model_validator

from core.enums import TipoMovimentacaoEnum

class TransacaoResponseSchema(SCBaseModel):
    id: int
    movimento: TipoMovimentacaoEnum
    data: datetime
    quantidade: Decimal
    tipo: str
    usuario_id: int
    usuario_nome: str
    lote_id: int
    lote_numero: str
    estoque_id: Optional[int]
    fornecedor_id: Optional[int]
    fornecedor_nome: Optional[str]
    preco_unitario: Optional[Decimal]
    observacao: Optional[str]

class TransacaoListResponseSchema(SCBaseModel):
    items: List[TransacaoResponseSchema]
    total: int
    page: int
    per_page: int

class TransacaoFilterSchema(SCBaseModel):
    search: Optional[str] = None
    movimento: Optional[TipoMovimentacaoEnum] = None
    tipo: Optional[str] = None
    usuario_id: Optional[int] = Field(default=None, gt=0)
    quantidade: Optional[Decimal] = Field(default=None, gt=0)
    quantidade_min: Optional[Decimal] = Field(default=None, ge=0)
    quantidade_max: Optional[Decimal] = Field(default=None, ge=0)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def validar_filtros(self):
        if (
            self.quantidade_min is not None
            and self.quantidade_max is not None
            and self.quantidade_min > self.quantidade_max
        ):
            raise ValueError("quantidade_min não pode ser maior que quantidade_max.")

        if (
            self.data_inicio is not None
            and self.data_fim is not None
            and self.data_inicio > self.data_fim
        ):
            raise ValueError("data_inicio não pode ser maior que data_fim.")

        return self