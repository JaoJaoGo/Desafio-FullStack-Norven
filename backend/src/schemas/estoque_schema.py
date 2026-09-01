from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel as SCBaseModel, Field

class LocalizacaoEstoqueSchema(SCBaseModel):
    corredor: str = Field(min_length=1, max_length=30)
    prateleira: str = Field(min_length=1, max_length=30)
    secao: str = Field(min_length=1, max_length=30)

class EstoqueUpdateSchema(SCBaseModel):
    corredor: Optional[str] = Field(default=None, min_length=1, max_length=30)
    prateleira: Optional[str] = Field(default=None, min_length=1, max_length=30)
    secao: Optional[str] = Field(default=None, min_length=1, max_length=30)
    localizacao: Optional[LocalizacaoEstoqueSchema] = None

class EstoqueResponseSchema(SCBaseModel):
    id: int
    quantidade_atual: Decimal
    corredor: str
    prateleira: str
    secao: str
    entrada_id: int
    lote_id: int
    lote_numero: str
    produto_id: int
    produto_nome: str

class EstoqueListResponseSchema(SCBaseModel):
    items: List[EstoqueResponseSchema]
    total: int
    page: int
    per_page: int

class EstoqueFilterSchema(SCBaseModel):
    search: Optional[str] = None
    produto_id: Optional[int] = Field(default=None, gt=0)
    lote_id: Optional[int] = Field(default=None, gt=0)
    somente_com_saldo: bool = False
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)