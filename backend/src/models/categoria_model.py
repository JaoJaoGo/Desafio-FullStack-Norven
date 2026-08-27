from typing import List
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings

class CategoriaModel(settings.DBBaseModel):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    produtos: Mapped[List["ProdutoModel"]] = relationship("ProdutoModel", back_populates="categoria")