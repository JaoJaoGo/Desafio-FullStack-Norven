from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel as SCBaseModel, Field, model_validator

from core.enums import TipoSaidaEnum

class SaidaBaseSchema(SCBaseModel):
    quantidade: Decimal = Field(gt=0, max_digits=12, decimal_places=3)
    preco_venda_unitario: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    estoque_id: int
    tipo_saida: TipoSaidaEnum

    @model_validator(mode="after")
    def validar_preco_saida(self):
        if (
            self.tipo_saida == TipoSaidaEnum.VENDA
            and self.preco_venda_unitario is None
        ):
            raise ValueError(
                "O preço de venda é obrigatório para saídas do tipo VENDA."
            )

        if (
            self.tipo_saida != TipoSaidaEnum.VENDA
            and self.preco_venda_unitario is not None
        ):
            raise ValueError(
                "O preço de venda deve ser nulo quando a saída não for do tipo VENDA."
            )

        return self

class SaidaCreateSchema(SaidaBaseSchema):
    pass

class SaidaUpdateSchema(SCBaseModel):
    data_saida: Optional[datetime] = None
    quantidade: Optional[Decimal] = Field(default=None, gt=0, max_digits=12, decimal_places=3)
    preco_venda_unitario: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    estoque_id: Optional[int] = None
    tipo_saida: Optional[TipoSaidaEnum] = None


class SaidaResponseSchema(SaidaBaseSchema):
    id: int
    data_saida: datetime

    class Config:
        from_attributes = True