from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel as SCBaseModel, ConfigDict, EmailStr, Field, model_validator

from core.enums import ProdutoStatusEnum
from schemas.categoria_schema import CategoriaResponseSchema
from schemas.estoque_schema import EstoqueResponseSchema
from schemas.informacao_nutricional_schema import InformacaoNutricionalCreateSchema, InformacaoNutricionalResponseSchema
from schemas.lote_schema import LoteResponseSchema
from schemas.unidade_medida_schema import UnidadeMedidaResponseSchema

class ProdutoBaseSchema(SCBaseModel):
    cod_idt: str = Field(min_length=1, max_length=50)
    nome: str = Field(min_length=1, max_length=50)
    descricao: Optional[str] = None
    preco_venda_atual: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    eh_perecivel: bool
    categoria_id: int = Field(gt=0)
    unidade_medida_id: int = Field(gt=0)

class ProdutoCreateSchema(ProdutoBaseSchema):
    informacao_nutricional: Optional[InformacaoNutricionalCreateSchema] = None

class ProdutoListItemSchema(SCBaseModel):
    id: int
    cod_idt: str
    nome: str
    preco_venda_atual: Decimal
    eh_perecivel: bool

    categoria_id: int
    categoria: str

    unidade_medida_id: int
    unidade_medida: str
    unidade_medida_sigla: str

    validade: Optional[date]

    estoque_total: Decimal
    estoque_baixo: bool

    status: ProdutoStatusEnum

class ProdutoFilterSchema(SCBaseModel):
    nome: Optional[str] = None
    categoria_id: Optional[int] = None
    categoria: Optional[str] = None
    status: Optional[ProdutoStatusEnum] = None
    preco_min: Optional[Decimal] = Field(default=None, ge=0)
    preco_max: Optional[Decimal] = Field(default=None, ge=0)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def validar_intervalo_preco(self):
        if (
            self.preco_min is not None
            and self.preco_max is not None
            and self.preco_min > self.preco_max
        ):
            raise ValueError("preco_min não pode ser maior que preco_max.")

        return self

class ProdutoUpdateSchema(SCBaseModel):
    cod_idt: Optional[str] = Field(default=None, min_length=1, max_length=50)
    nome: Optional[str] = Field(default=None, min_length=1, max_length=50)
    descricao: Optional[str] = None
    preco_venda_atual: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    eh_perecivel: Optional[bool] = None
    categoria_id: Optional[int] = Field(default=None, gt=0)
    unidade_medida_id: Optional[int] = Field(default=None, gt=0)
    informacao_nutricional: Optional[InformacaoNutricionalCreateSchema] = None

class UsuarioProdutoResumoSchema(SCBaseModel):
    id: int
    nome: str
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True
    )

class ProdutoListResponseSchema(SCBaseModel):
    items: List[ProdutoListItemSchema]
    total: int
    page: int
    per_page: int

class ProdutoDetailResponseSchema(SCBaseModel):
    id: int
    cod_idt: str
    nome: str
    descricao: Optional[str]
    preco_venda_atual: Decimal
    eh_perecivel: bool
    data_cadastro: datetime
    usuario_id: int
    categoria_id: int
    unidade_medida_id: int
    informacao_nutricional_id: Optional[int]
    responsavel: UsuarioProdutoResumoSchema
    categoria: CategoriaResponseSchema
    unidade_medida: UnidadeMedidaResponseSchema
    informacao_nutricional: Optional[InformacaoNutricionalResponseSchema]
    validade: Optional[date]
    estoque_total: Decimal
    estoque_baixo: bool
    status: ProdutoStatusEnum
    lotes: List[LoteResponseSchema]
    estoques: List[EstoqueResponseSchema]