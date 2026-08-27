from typing import List
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings

class UnidadeMedidaModel(settings.DBBaseModel):
    __tablename__ = "unidades_medidas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    sigla: Mapped[str] = mapped_column(String(5), nullable=False, unique=True)

    produtos: Mapped[List["ProdutoModel"]] = relationship("ProdutoModel", back_populates="unidade_medida")
    informacoes_nutricionais: Mapped[List["InformacaoNutricionalModel"]] = relationship("InformacaoNutricionalModel", back_populates="unidade_porcao")