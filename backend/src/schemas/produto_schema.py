from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel as SCBaseModel, Field

class ProdutoBaseSchema(SCBaseModel):
    cod_idt: str = Field(min_length=1, max_length=50)
    nome: str = Field(min_length=1, max_length=50)
    descricao: Optional[str] = None
    preco_venda_atual: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    usuario_id: int
    categoria_id: int
    unidade_medida_id: int
    informacao_nutricional_id: Optional[int] = None


class ProdutoCreateSchema(ProdutoBaseSchema):
    pass


class ProdutoUpdateSchema(SCBaseModel):
    cod_idt: Optional[str] = Field(default=None, min_length=1, max_length=50)
    nome: Optional[str] = Field(default=None, min_length=1, max_length=50)
    descricao: Optional[str] = None
    preco_venda_atual: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    usuario_id: Optional[int] = None
    categoria_id: Optional[int] = None
    unidade_medida_id: Optional[int] = None
    informacao_nutricional_id: Optional[int] = None


class ProdutoResponseSchema(ProdutoBaseSchema):
    id: int
    data_cadastro: datetime

    class Config:
        from_attributes = True