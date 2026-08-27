from decimal import Decimal
from typing import List, Optional
from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings

class InformacaoNutricionalModel(settings.DBBaseModel):
    __tablename__ = "informacoes_nutricionais"

    __table_args__ = (
        CheckConstraint(
            "porcao_quantidade > 0",
            name="ck_in_porcao_quantidade"
        ),
        CheckConstraint(
            "valor_energetico_kcal >= 0",
            name="ck_in_valor_energetico"
        ),
        CheckConstraint(
            "carboidratos_g >= 0",
            name="ck_in_carboidratos"
        ),
        CheckConstraint(
            "proteinas_g >= 0",
            name="ck_in_proteinas"
        ),
        CheckConstraint(
            "gorduras_totais_g >= 0",
            name="ck_in_gorduras_totais"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    porcao_quantidade: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    valor_energetico_kcal: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    carboidratos_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    proteinas_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    gorduras_totais_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    ingredientes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    alergenicos: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unidade_porcao_id: Mapped[int] = mapped_column("id_unidade_porcao", Integer, ForeignKey("unidades_medidas.id"), nullable=False)

    unidade_porcao: Mapped["UnidadeMedidaModel"] = relationship("UnidadeMedidaModel", back_populates="informacoes_nutricionais")
    produtos: Mapped[List["ProdutoModel"]] = relationship("ProdutoModel", back_populates="informacao_nutricional")
