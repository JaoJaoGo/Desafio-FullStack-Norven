from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import CheckConstraint, DateTime, Enum as SqlEnum, ForeignKey, Index, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings
from core.enums import TipoSaidaEnum


class SaidaModel(settings.DBBaseModel):
    __tablename__ = "saidas"

    __table_args__ = (
        CheckConstraint(
            "quantidade > 0",
            name="ck_saida_quantidade"
        ),
        CheckConstraint(
            """
            tipo_saida IN (
                'VENDA',
                'PERDA',
                'AVARIA',
                'VENCIMENTO',
                'RECALL'
            )
            """,
            name="ck_saida_tipo"
        ),
        CheckConstraint(
            """
            (
                tipo_saida = 'VENDA'
                AND preco_venda_unitario IS NOT NULL
            )
            OR
            (
                tipo_saida <> 'VENDA'
                AND preco_venda_unitario IS NULL
            )
            """,
            name="ck_saida_preco"
        ),
        Index(
            "idx_saida_id_estoque",
            "id_estoque"
        ),
        Index(
            "idx_saida_data_saida",
            "data_saida"
        ),
        Index(
            "idx_saida_tipo_data",
            "tipo_saida",
            "data_saida"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    data_saida: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    quantidade: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    preco_venda_unitario: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    estoque_id: Mapped[int] = mapped_column("id_estoque", Integer, ForeignKey("estoques.id"), nullable=False)
    tipo_saida: Mapped[TipoSaidaEnum] = mapped_column(
        SqlEnum(
            TipoSaidaEnum,
            native_enum=False,
            create_constraint=False,
            values_callable=lambda enum: [item.value for item in enum],
            length=30
        ),
        nullable=False
    )

    estoque: Mapped["EstoqueModel"] = relationship("EstoqueModel", back_populates="saidas")
