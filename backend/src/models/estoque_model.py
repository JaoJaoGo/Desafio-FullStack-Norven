from decimal import Decimal
from typing import List
from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings

class EstoqueModel(settings.DBBaseModel):
    __tablename__ = "estoques"

    __table_args__ = (
        CheckConstraint(
            "quantidade_atual >= 0",
            name="ck_estoque_quantidade"
        ),
        Index(
            "idx_estoque_id_entrada",
            "id_entrada"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quantidade_atual: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    corredor: Mapped[str] = mapped_column(String(30), nullable=False)
    prateleira: Mapped[str] = mapped_column(String(30), nullable=False)
    secao: Mapped[str] = mapped_column(String(30), nullable=False)
    entrada_id: Mapped[int] = mapped_column("id_entrada", Integer, ForeignKey("entradas.id"), nullable=False)

    entrada: Mapped["EntradaModel"] = relationship("EntradaModel", back_populates="estoques")
    saidas: Mapped[List["SaidaModel"]] = relationship("SaidaModel", back_populates="estoque")