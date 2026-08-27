"""create pais estado cidade

Revision ID: 001
Revises:
Create Date: 2026-08-27 09:55
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import UserDefinedType

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

class PostgreSQLPoint(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw):
        return "POINT"

def upgrade() -> None:
    # ------------------------------
    # PAIS
    # ------------------------------
    op.create_table(
        "pais",

        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            nullable=False
        ),

        sa.Column(
            "nome",
            sa.String(length=60),
            nullable=True
        ),

        sa.Column(
            "nome_pt",
            sa.String(length=60),
            nullable=True
        ),

        sa.Column(
            "sigla",
            sa.String(length=2),
            nullable=True
        ),

        sa.Column(
            "bacen",
            sa.Integer(),
            nullable=True
        ),

        sa.Column(
            "ddi",
            sa.Integer(),
            nullable=True
        ),

        sa.PrimaryKeyConstraint("id")
    )

    # ------------------------------
    # ESTADO
    # ------------------------------
    op.create_table(
        "estado",

        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            nullable=False
        ),

        sa.Column(
            "nome",
            sa.String(length=60),
            nullable=True
        ),

        sa.Column(
            "uf",
            sa.String(length=2),
            nullable=True
        ),

        sa.Column(
            "ibge",
            sa.Integer(),
            nullable=True
        ),

        sa.Column(
            "pais",
            sa.BigInteger(),
            nullable=True
        ),

        sa.Column(
            "ddd",
            sa.JSON(),
            nullable=True
        ),

        sa.ForeignKeyConstraint(
            ["pais"],
            ["pais.id"],
            name="fk_estado_pais"
        ),

        sa.PrimaryKeyConstraint("id")
    )

    # ------------------------------
    # CIDADE
    # ------------------------------
    op.create_table(
        "cidade",

        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            nullable=False
        ),

        sa.Column(
            "nome",
            sa.String(length=120),
            nullable=True
        ),

        sa.Column(
            "uf",
            sa.BigInteger(),
            nullable=True
        ),

        sa.Column(
            "ibge",
            sa.Integer(),
            nullable=True
        ),

        sa.Column(
            "lat_lon",
            PostgreSQLPoint(),
            nullable=True
        ),

        sa.Column(
            "cod_tom",
            sa.SmallInteger(),
            server_default=sa.text("0"),
            nullable=True
        ),

        sa.ForeignKeyConstraint(
            ["uf"],
            ["estado.id"],
            name="fk_cidade_estado"
        ),

        sa.PrimaryKeyConstraint("id")
    )

    # Índices das FKs
    op.create_index(
        "idx_estado_pais",
        "estado",
        ["pais"]
    )

    op.create_index(
        "idx_cidade_uf",
        "cidade",
        ["uf"]
    )

    op.create_index(
        "idx_cidade_nome_uf",
        "cidade",
        ["nome", "uf"]
    )

def downgrade() -> None:
    op.drop_index(
        "idx_cidade_nome_uf",
        table_name="cidade"
    )

    op.drop_index(
        "idx_cidade_uf",
        table_name="cidade"
    )

    op.drop_index(
        "idx_estado_pais",
        table_name="estado"
    )

    op.drop_table("cidade")
    op.drop_table("estado")
    op.drop_table("pais")