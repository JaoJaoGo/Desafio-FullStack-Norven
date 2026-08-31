from typing import List
from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings
from core.enums import NivelAcessoEnum


class UsuarioModel(settings.DBBaseModel):
    __tablename__ = "funcionarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column("senha", String(255), nullable=False)
    nivel_acesso: Mapped[NivelAcessoEnum] = mapped_column(
        Enum(
            NivelAcessoEnum,
            name="nivel_acesso_enum",
            values_callable=lambda enum: [
                item.value for item in enum
            ]
        ),
        nullable=False
    )
    endereco_id: Mapped[int] = mapped_column("id_endereco", Integer, ForeignKey("enderecos.id"), nullable=False)
    contato_id: Mapped[int] = mapped_column("id_contato", Integer, ForeignKey("contatos.id"), nullable=False, unique=True)
    
    endereco: Mapped["EnderecoModel"] = relationship("EnderecoModel", back_populates="usuarios")
    contato: Mapped["ContatoModel"] = relationship("ContatoModel", back_populates="usuario", uselist=False)
    produtos: Mapped[List["ProdutoModel"]] = relationship("ProdutoModel", back_populates="usuario")
    entradas: Mapped[List["EntradaModel"]] = relationship("EntradaModel", back_populates="usuario")
    saidas: Mapped[List["SaidaModel"]] = relationship("SaidaModel", back_populates="usuario")