"""adiciona auditoria nas movimentacoes

Revision ID: ebb0d07a7a6b
Revises: 78b1522cfaef
Create Date: 2026-08-30 11:39:41.913814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebb0d07a7a6b'
down_revision: Union[str, Sequence[str], None] = '78b1522cfaef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "entradas",
        sa.Column(
            "tipo_entrada",
            sa.String(30),
            nullable=True
        )
    )

    op.add_column(
        "entradas",
        sa.Column(
            "observacao",
            sa.Text(),
            nullable=True
        )
    )

    op.add_column(
        "entradas",
        sa.Column(
            "id_funcionario",
            sa.Integer(),
            nullable=True
        )
    )

    op.create_foreign_key(
        "fk_entrada_id_funcionario",
        "entradas",
        "funcionarios",
        ["id_funcionario"],
        ["id"]
    )

    op.add_column(
        "saidas",
        sa.Column(
            "id_funcionario",
            sa.Integer(),
            nullable=True
        )
    )

    op.create_foreign_key(
        "fk_saida_id_funcionario",
        "saidas",
        "funcionarios",
        ["id_funcionario"],
        ["id"]
    )

    op.execute(
        """
        UPDATE entradas
        SET tipo_entrada = 'NAO_INFORMADO'
        WHERE tipo_entrada IS NULL
        """
    )

    op.execute(
        """
        UPDATE entradas
        SET id_funcionario = (
            SELECT id
            FROM funcionarios
            ORDER BY id
            LIMIT 1
        )
        WHERE id_funcionario IS NULL
        """
    )

    op.execute(
        """
        UPDATE saidas
        SET id_funcionario = (
            SELECT id
            FROM funcionarios
            ORDER BY id
            LIMIT 1
        )
        WHERE id_funcionario IS NULL
        """
    )

    connection = op.get_bind()

    entradas_sem_usuario = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM entradas
            WHERE id_funcionario IS NULL
            """
        )
    ).scalar()

    saidas_sem_usuario = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM saidas
            WHERE id_funcionario IS NULL
            """
        )
    ).scalar()

    if entradas_sem_usuario or saidas_sem_usuario:
        raise RuntimeError(
            "Existem movimentações antigas sem funcionário "
            "e nenhum funcionário disponível para backfill."
        )

    op.alter_column(
        "entradas",
        "tipo_entrada",
        nullable=False
    )

    op.alter_column(
        "entradas",
        "id_funcionario",
        nullable=False
    )

    op.alter_column(
        "saidas",
        "id_funcionario",
        nullable=False
    )

    op.create_index(
        "idx_entrada_id_funcionario",
        "entradas",
        ["id_funcionario"]
    )

    op.create_index(
        "idx_entrada_tipo_data",
        "entradas",
        ["tipo_entrada", "data_entrada"]
    )

    op.create_index(
        "idx_saida_id_funcionario",
        "saidas",
        ["id_funcionario"]
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS
        trg_saida_movimenta_estoque
        ON saidas
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "idx_saida_id_funcionario",
        table_name="saidas"
    )

    op.drop_index(
        "idx_entrada_tipo_data",
        table_name="entradas"
    )

    op.drop_index(
        "idx_entrada_id_funcionario",
        table_name="entradas"
    )

    op.drop_constraint(
        "fk_saida_id_funcionario",
        "saidas",
        type_="foreignkey"
    )

    op.drop_constraint(
        "fk_entrada_id_funcionario",
        "entradas",
        type_="foreignkey"
    )

    op.drop_column(
        "saidas",
        "id_funcionario"
    )

    op.drop_column(
        "entradas",
        "id_funcionario"
    )

    op.drop_column(
        "entradas",
        "observacao"
    )

    op.drop_column(
        "entradas",
        "tipo_entrada"
    )