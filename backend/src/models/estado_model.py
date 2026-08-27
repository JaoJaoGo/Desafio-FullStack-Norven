from typing import List, Optional
from sqlalchemy import BigInteger, Integer, String, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings

class EstadoModel(settings.DBBaseModel):
    __tablename__ = "estado"

    __table_args__ = (
        Index("idx_estado_pais", "pais"),
    )
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    uf: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    ibge: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pais_id: Mapped[Optional[int]] = mapped_column("pais", BigInteger, ForeignKey("pais.id"), nullable=True)
    ddd: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    pais: Mapped[Optional["PaisModel"]] = relationship("PaisModel", back_populates="estados")
    cidades: Mapped[List["CidadeModel"]] = relationship("CidadeModel", back_populates="estado")