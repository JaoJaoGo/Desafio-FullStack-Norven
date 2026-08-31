from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel as SCBaseModel, Field, model_validator

from core.enums import TipoSaidaEnum

class SaidaCreateBaseSchema(SCBaseModel):
    estoque_id: int = Field(gt=0)
    quantidade: Decimal = Field(gt=0, max_digits=12, decimal_places=3)
    tipo_saida: TipoSaidaEnum
    preco_venda_unitario: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    data_saida: Optional[datetime] = None

    @model_validator(mode="after")
    def validar_preco(self):
        if (
            self.tipo_saida != TipoSaidaEnum.VENDA
            and self.preco_venda_unitario is not None
        ):
            raise ValueError("Somente saídas do tipo VENDA podem possuir preço de venda.")

        return self

class SaidaCreateSchema(SaidaCreateBaseSchema):
    produto_id: int = Field(gt=0)

class ProdutoSaidaCreateSchema(SaidaCreateBaseSchema):
    pass

class SaidaUpdateSchema(SCBaseModel):
    quantidade: Optional[Decimal] = Field(default=None, gt=0, max_digits=12, decimal_places=3)
    tipo_saida: Optional[TipoSaidaEnum] = None
    preco_venda_unitario: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    data_saida: Optional[datetime] = None

class SaidaResponseSchema(SCBaseModel):
    id: int
    data_saida: datetime
    quantidade: Decimal
    tipo_saida: TipoSaidaEnum
    preco_venda_unitario: Optional[Decimal]
    estoque_id: int
    lote_id: int
    lote_numero: str
    produto_id: int
    produto_nome: str
    usuario_id: int
    usuario_nome: str

class SaidaListResponseSchema(SCBaseModel):
    items: List[SaidaResponseSchema]
    total: int
    page: int
    per_page: int


class SaidaFilterSchema(SCBaseModel):
    search: Optional[str] = None
    produto_id: Optional[int] = Field(default=None, gt=0)
    usuario_id: Optional[int] = Field(default=None, gt=0)
    tipo_saida: Optional[TipoSaidaEnum] = None
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
            raise ValueError("quantidade_min não pode ser maior que quantidade_max")

        if (
            self.data_inicio is not None
            and self.data_fim is not None
            and self.data_inicio > self.data_fim
        ):
            raise ValueError("data_inicio não pode ser maior que data_fim")

        return self