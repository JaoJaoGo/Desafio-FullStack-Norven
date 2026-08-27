from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings

class EntradaModel(settings.DBBaseModel):
    __tablename__ = "entradas"

    __table_args__ = (
        CheckConstraint(
            "quantidade > 0",
            name="ck_entrada_quantidade"
        ),
        CheckConstraint(
            "preco_custo_unitario >= 0",
            name="ck_entrada_preco_custo"
        ),
        Index(
            "idx_entrada_id_lote",
            "id_lote"
        ),
        Index(
            "idx_entrada_id_fornecedor",
            "id_fornecedor"
        ),
        Index(
            "idx_entrada_data_entrada",
            "data_entrada"
        ),
        Index(
            "idx_entrada_fornecedor_data",
            "id_fornecedor",
            "data_entrada"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    data_entrada: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    quantidade: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    preco_custo_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fornecedor_id: Mapped[int] = mapped_column("id_fornecedor", Integer, ForeignKey("fornecedores.id"), nullable=False)
    lote_id: Mapped[int] = mapped_column("id_lote", Integer, ForeignKey("lotes.id"), nullable=False)

    fornecedor: Mapped["FornecedorModel"] = relationship("FornecedorModel", back_populates="entradas")
    lote: Mapped["LoteModel"] = relationship("LoteModel", back_populates="entradas")
    estoques: Mapped[List["EstoqueModel"]] = relationship("EstoqueModel", back_populates="entrada")
