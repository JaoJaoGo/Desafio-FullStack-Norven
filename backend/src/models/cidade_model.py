from typing import Optional
from sqlalchemy import BigInteger, Integer, String, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import UserDefinedType

from core.configs import settings

class PostgreSQLPoint(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw):
        return "POINT"

class CidadeModel(settings.DBBaseModel):
    __tablename__ = "cidade"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    estado_id: Mapped[Optional[int]] = mapped_column("uf", BigInteger, ForeignKey("estado.id"), nullable=True)
    ibge: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lat_lon: Mapped[Optional[object]] = mapped_column(PostgreSQLPoint(), nullable=True)
    cod_tom: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, server_default="0")
    
    estado: Mapped[Optional["EstadoModel"]] = relationship("EstadoModel", back_populates="cidades")