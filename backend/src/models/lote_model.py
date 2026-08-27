from datetime import date
from typing import List
from sqlalchemy import Date, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings

class LoteModel(settings.DBBaseModel):
    __tablename__ = "lotes"

    __table_args__ = (
        UniqueConstraint(
            "id_produto",
            "numero",
            name="un_lote_produto_numero"
        ),
        Index(
            "idx_lote_numero",
            "numero"
        ),
        Index(
            "idx_lote_data_validade",
            "data_validade"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero: Mapped[str] = mapped_column(String(30), nullable=False)
    data_validade: Mapped[date] = mapped_column(Date, nullable=False)
    produto_id: Mapped[int] = mapped_column("id_produto", Integer, ForeignKey("produtos.id"), nullable=False)

    produto: Mapped["ProdutoModel"] = relationship("ProdutoModel", back_populates="lotes")
    entradas: Mapped[List["EntradaModel"]] = relationship("EntradaModel", back_populates="lote")