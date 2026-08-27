from typing import List, Optional

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings

class ContatoModel(settings.DBBaseModel):
    __tablename__ = "contatos"

    __table_args__ = (UniqueConstraint("cod_pais", "ddd", "numero", name="un_contato_telefone"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cod_pais: Mapped[str] = mapped_column(String(30), nullable=False)
    ddd: Mapped[str] = mapped_column(String(3), nullable=False)
    numero: Mapped[str] = mapped_column(String(30), nullable=False)
    
    usuario: Mapped[Optional["UsuarioModel"]] = relationship("UsuarioModel", back_populates="contato", uselist=False)
    fornecedores: Mapped[List["FornecedorModel"]] = relationship("FornecedorModel", back_populates="contato")
