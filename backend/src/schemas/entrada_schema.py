from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel as SCBaseModel, Field, model_validator

from schemas.estoque_schema import LocalizacaoEstoqueSchema
from schemas.lote_schema import LoteInlineCreateSchema

class EntradaCreateBaseSchema(SCBaseModel):
    fornecedor_id: int = Field(gt=0)
    lote_id: Optional[int] = Field(default=None, gt=0)
    novo_lote: Optional[LoteInlineCreateSchema] = None
    quantidade: Decimal = Field(gt=0, max_digits=12, decimal_places=3)
    preco_custo_unitario: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    tipo_entrada: str = Field(min_length=1, max_length=30)
    observacao: Optional[str] = None
    data_entrada: Optional[datetime] = None
    localizacao: LocalizacaoEstoqueSchema

    @model_validator(mode="after")
    def validar_lote(self):
        if self.lote_id is None and self.novo_lote is None:
            raise ValueError("Informe lote_id ou novo_lote.")

        if self.lote_id is not None and self.novo_lote is not None:
            raise ValueError("Informe apenas lote_id ou novo_lote.")

        return self

class EntradaCreateSchema(EntradaCreateBaseSchema):
    produto_id: int = Field(gt=0)

class ProdutoEntradaCreateSchema(EntradaCreateBaseSchema):
    pass

class EntradaUpdateSchema(SCBaseModel):
    fornecedor_id: Optional[int] = Field(default=None, gt=0)
    quantidade: Optional[Decimal] = Field(default=None, gt=0, max_digits=12, decimal_places=3)
    preco_custo_unitario: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    tipo_entrada: Optional[str] = Field(default=None, min_length=1, max_length=30)
    observacao: Optional[str] = None
    data_entrada: Optional[datetime] = None
    localizacao: Optional[LocalizacaoEstoqueSchema] = None

class EntradaResponseSchema(SCBaseModel):
    id: int
    data_entrada: datetime
    quantidade: Decimal
    preco_custo_unitario: Decimal
    tipo_entrada: str
    observacao: Optional[str]
    fornecedor_id: int
    fornecedor_nome: str
    lote_id: int
    lote_numero: str
    produto_id: int
    produto_nome: str
    usuario_id: int
    usuario_nome: str
    estoque_id: int
    quantidade_atual: Decimal
    corredor: str
    prateleira: str
    secao: str

class EntradaListResponseSchema(SCBaseModel):
    items: List[EntradaResponseSchema]
    total: int
    page: int
    per_page: int


class EntradaFilterSchema(SCBaseModel):
    search: Optional[str] = None
    produto_id: Optional[int] = Field(default=None, gt=0)
    fornecedor_id: Optional[int] = Field(default=None, gt=0)
    usuario_id: Optional[int] = Field(default=None, gt=0)
    tipo_entrada: Optional[str] = None
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