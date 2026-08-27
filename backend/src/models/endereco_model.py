from typing import List, Optional
from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings

class EnderecoModel(settings.DBBaseModel):
    __tablename__ = "enderecos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    logradouro: Mapped[str] = mapped_column(String(50), nullable=False)
    numero: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    complemento: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cep: Mapped[str] = mapped_column(String(11), nullable=False)
    bairro: Mapped[str] = mapped_column(String(30), nullable=False)
    municipio_id: Mapped[int] = mapped_column("id_municipio", BigInteger, ForeignKey("cidade.id"), nullable=False)

    municipio: Mapped["CidadeModel"] = relationship("CidadeModel", back_populates="enderecos")
    usuarios: Mapped[List["UsuarioModel"]] = relationship("UsuarioModel", back_populates="endereco")
    fornecedores: Mapped[List["FornecedorModel"]] = relationship("FornecedorModel", back_populates="endereco")
    