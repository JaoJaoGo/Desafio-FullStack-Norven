from sqlalchemy import CHAR, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings


class FornecedorModel(settings.DBBaseModel):
    __tablename__ = "fornecedores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    cnpj: Mapped[str] = mapped_column(CHAR(14), nullable=False, unique=True)
    endereco_id: Mapped[int] = mapped_column("id_endereco", Integer, ForeignKey("enderecos.id"), nullable=False)
    contato_id: Mapped[int] = mapped_column("id_contato", Integer, ForeignKey("contatos.id"), nullable=False)

    endereco: Mapped["EnderecoModel"] = relationship("EnderecoModel", back_populates="fornecedores")
    contato: Mapped["ContatoModel"] = relationship("ContatoModel", back_populates="fornecedores")