"""adiciona perecibilidade aos produtos

Revision ID: 78b1522cfaef
Revises: 6927cfe11206
Create Date: 2026-08-29 19:41:02.655010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78b1522cfaef'
down_revision: Union[str, Sequence[str], None] = '6927cfe11206'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "produtos",
        sa.Column(
            "eh_perecivel",
            sa.Boolean(),
            nullable=True,
            server_default=sa.text("false")
        )
    )

    op.execute(
        """
        UPDATE produtos p
        SET eh_perecivel = EXISTS (
            SELECT 1
            FROM lotes l
            WHERE l.id_produto = p.id
        )
        """
    )

    op.alter_column(
        "produtos",
        "eh_perecivel",
        existing_type=sa.Boolean(),
        nullable=False
    )

    op.alter_column(
        "lotes",
        "data_validade",
        existing_type=sa.Date(),
        nullable=True
    )

    # ---------------------------------------------------------
    # TRIGGER:
    # lote de produto perecível exige validade
    # ---------------------------------------------------------

    op.execute(
        """
        CREATE OR REPLACE FUNCTION
        fn_validar_validade_lote_perecivel()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_eh_perecivel boolean;
        BEGIN
            SELECT eh_perecivel
            INTO v_eh_perecivel
            FROM produtos
            WHERE id = NEW.id_produto;

            IF NOT FOUND THEN
                RAISE EXCEPTION
                    'Produto % não encontrado.',
                    NEW.id_produto;
            END IF;

            IF v_eh_perecivel
               AND NEW.data_validade IS NULL THEN

                RAISE EXCEPTION
                    'Produtos perecíveis exigem data de validade.';
            END IF;

            RETURN NEW;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_lote_validade_perecivel
        BEFORE INSERT OR UPDATE OF data_validade, id_produto
        ON lotes
        FOR EACH ROW
        EXECUTE FUNCTION fn_validar_validade_lote_perecivel();
        """
    )

     # ---------------------------------------------------------
    # TRIGGER:
    # impede transformar produto em perecível caso possua
    # lote sem data de validade.
    # ---------------------------------------------------------

    op.execute(
        """
        CREATE OR REPLACE FUNCTION
        fn_validar_produto_perecivel()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF NEW.eh_perecivel = true
               AND OLD.eh_perecivel = false THEN

                IF EXISTS (
                    SELECT 1
                    FROM lotes
                    WHERE id_produto = NEW.id
                      AND data_validade IS NULL
                ) THEN

                    RAISE EXCEPTION
                        'Produto não pode ser marcado como perecível: existem lotes sem data de validade.';
                END IF;

            END IF;

            RETURN NEW;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_produto_perecivel
        BEFORE UPDATE OF eh_perecivel
        ON produtos
        FOR EACH ROW
        EXECUTE FUNCTION fn_validar_produto_perecivel();
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP TRIGGER IF EXISTS
        trg_produto_perecivel
        ON produtos;
        """
    )

    op.execute(
        """
        DROP FUNCTION IF EXISTS
        fn_validar_produto_perecivel();
        """
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS
        trg_lote_validade_perecivel
        ON lotes;
        """
    )

    op.execute(
        """
        DROP FUNCTION IF EXISTS
        fn_validar_validade_lote_perecivel();
        """
    )

    connection = op.get_bind()

    possui_validade_nula = connection.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM lotes
                WHERE data_validade IS NULL
            )
            """
        )
    ).scalar()

    if possui_validade_nula:
        raise RuntimeError(
            "Não é possível realizar downgrade: "
            "existem lotes com data_validade NULL."
        )

    op.alter_column(
        "lotes",
        "data_validade",
        existing_type=sa.Date(),
        nullable=False
    )

    op.drop_column(
        "produtos",
        "eh_perecivel"
    )
