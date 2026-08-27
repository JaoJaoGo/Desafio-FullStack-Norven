from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.configs import settings

class ProdutoModel(settings.DBBaseModel):
    __tablename__ = "produtos"

    __table_args__ = (
        CheckConstraint(
            "preco_venda_atual >= 0",
            name="ck_produto_preco_venda"
        ),

        Index(
            "idx_produto_id_funcionario",
            "id_funcionario"
        ),

        Index(
            "idx_produto_id_categoria",
            "id_categoria"
        ),

        Index(
            "idx_produto_id_unidade_medida",
            "id_unidade_medida"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cod_idt: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preco_venda_atual: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    data_cadastro: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    usuario_id: Mapped[int] = mapped_column("id_funcionario", Integer, ForeignKey("funcionarios.id"), nullable=False)
    categoria_id: Mapped[int] = mapped_column("id_categoria", Integer, ForeignKey("categorias.id"), nullable=False)
    unidade_medida_id: Mapped[int] = mapped_column("id_unidade_medida", Integer, ForeignKey("unidades_medidas.id"), nullable=False)
    informacao_nutricional_id: Mapped[Optional[int]] = mapped_column("id_inf_nut", Integer, ForeignKey("informacoes_nutricionais.id"), nullable=True)

    usuario: Mapped["UsuarioModel"] = relationship("UsuarioModel", back_populates="produtos")
    categoria: Mapped["CategoriaModel"] = relationship("CategoriaModel", back_populates="produtos")
    unidade_medida: Mapped["UnidadeMedidaModel"] = relationship("UnidadeMedidaModel", back_populates="produtos")
    informacao_nutricional: Mapped[Optional["InformacaoNutricionalModel"]] = relationship("InformacaoNutricionalModel", back_populates="produtos")
