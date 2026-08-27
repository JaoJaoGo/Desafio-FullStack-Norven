from typing import List, Optional
from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings

class PaisModel(settings.DBBaseModel):
    __tablename__ = "pais"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    nome_pt: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    sigla: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    bacen: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ddi: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    estados: Mapped[List["EstadoModel"]] = relationship("EstadoModel", back_populates="pais")