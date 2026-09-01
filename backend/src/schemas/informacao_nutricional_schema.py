from decimal import Decimal
from typing import Optional
from pydantic import BaseModel as SCBaseModel, Field
from pydantic_settings import SettingsConfigDict

from schemas.unidade_medida_schema import UnidadeMedidaResponseSchema

class InformacaoNutricionalBaseSchema(SCBaseModel):
    porcao_quantidade: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    valor_energetico_kcal: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    carboidratos_g: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    proteinas_g: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    gorduras_totais_g: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    ingredientes: Optional[str] = None
    alergenicos: Optional[str] = None
    unidade_porcao_id: int = Field(gt=0)

class InformacaoNutricionalCreateSchema(InformacaoNutricionalBaseSchema):
    pass

class InformacaoNutricionalResponseSchema(InformacaoNutricionalBaseSchema):
    id: int
    unidade_porcao: UnidadeMedidaResponseSchema

    model_config = SettingsConfigDict(
        from_attributes=True
    )