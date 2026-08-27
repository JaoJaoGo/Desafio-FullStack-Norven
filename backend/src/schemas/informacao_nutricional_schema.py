from decimal import Decimal
from typing import Optional

from pydantic import BaseModel as SCBaseModel, Field


class InformacaoNutricionalBaseSchema(SCBaseModel):
    porcao_quantidade: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    valor_energetico_kcal: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    carboidratos_g: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    proteinas_g: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    gorduras_totais_g: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    ingredientes: Optional[str] = None
    alergenicos: Optional[str] = None
    unidade_porcao_id: int


class InformacaoNutricionalCreateSchema(InformacaoNutricionalBaseSchema):
    pass


class InformacaoNutricionalUpdateSchema(SCBaseModel):
    porcao_quantidade: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    valor_energetico_kcal: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    carboidratos_g: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    proteinas_g: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    gorduras_totais_g: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    ingredientes: Optional[str] = None
    alergenicos: Optional[str] = None
    unidade_porcao_id: Optional[int] = None


class InformacaoNutricionalResponseSchema(InformacaoNutricionalBaseSchema):
    id: int

    class Config:
        from_attributes = True