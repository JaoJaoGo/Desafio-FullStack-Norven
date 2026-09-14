from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.engine.result import Result
from sqlalchemy.sql.selectable import Select
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from seeders.bootstrap import SRC_DIR  # noqa: F401
from core.configs import settings
from core.enums import TipoSaidaEnum
from models.estoque_model import EstoqueModel
from models.saida_model import SaidaModel
from models.usuario_model import UsuarioModel


def _saida_specs() -> list[dict]:
    specs: list[dict] = []

    tipos: list[TipoSaidaEnum] = [
        TipoSaidaEnum.VENDA,
        TipoSaidaEnum.VENDA,
        TipoSaidaEnum.PERDA,
        TipoSaidaEnum.AVARIA,
        TipoSaidaEnum.RECALL,
        TipoSaidaEnum.VENDA,
    ]

    for index in range(1, 31):
        specs.append(
            {
                "entrada_code": f"E{index:03d}",
                "usuario_index": ((index + 2) % 12) + 1,
                "tipo_saida": tipos[(index - 1) % len(tipos)],
                "quantidade": Decimal(str(3 + (index % 5))),
                "days_ago": 50 - index,
            }
        )

    # Produto 003 sem estoque.
    specs[2]["quantidade"] = Decimal("20.000")

    # Produto 001 com estoque baixo.
    low_limit = Decimal(str(settings.ESTOQUE_BAIXO_LIMITE))

    target_balance: Decimal = low_limit if low_limit > 0 else Decimal("1")

    specs[0]["quantidade"] = max(Decimal("1"), Decimal("35") - target_balance)

    # Casos coerentes com validade.
    specs[5]["tipo_saida"] = TipoSaidaEnum.VENCIMENTO
    specs[5]["quantidade"] = Decimal("5.000")

    specs[6]["tipo_saida"] = TipoSaidaEnum.VENDA
    specs[6]["quantidade"] = Decimal("4.000")

    specs[11]["tipo_saida"] = TipoSaidaEnum.VENCIMENTO
    specs[11]["quantidade"] = Decimal("5.000")

    return specs

async def seed_saidas(session: AsyncSession, estoques: dict[str, EstoqueModel], usuarios: dict[str, UsuarioModel]) -> None:
    print("Seeding saídas...")

    usuario_list: list[UsuarioModel] = list(usuarios.values())

    if not usuario_list:
        raise RuntimeError("Usuários devem existir antes das saídas.")

    now: datetime = datetime.now().replace(
        hour=15,
        minute=0,
        second=0,
        microsecond=0,
    )

    for item in _saida_specs():
        estoque: EstoqueModel = estoques[item["entrada_code"]]

        usuario: UsuarioModel = usuario_list[item["usuario_index"] - 1]

        query: Select[tuple[SaidaModel]] = select(SaidaModel).where(
            SaidaModel.estoque_id == estoque.id,
            SaidaModel.usuario_id == usuario.id,
            SaidaModel.tipo_saida == item["tipo_saida"],
        )

        query_result: Result[tuple[SaidaModel]] = await session.execute(query)
        saida: SaidaModel | None = query_result.scalar_one_or_none()

        data_saida: datetime = now - timedelta(
            days=max(0, item["days_ago"])
        )

        quantidade: Decimal = item["quantidade"]

        if quantidade <= 0:
            quantidade = Decimal("1.000")

        preco: Decimal | None = Decimal("19.90") + Decimal(str(item["usuario_index"]))

        if item["tipo_saida"] != TipoSaidaEnum.VENDA:
            preco = None

        if saida is None:
            if quantidade > estoque.quantidade_atual:
                raise RuntimeError(f"Saldo insuficiente ao seedar saída de {item["entrada_code"]}.")

            estoque.quantidade_atual -= quantidade

            saida = SaidaModel(
                data_saida=data_saida,
                quantidade=quantidade,
                preco_venda_unitario=preco,
                estoque_id=estoque.id,
                usuario_id=usuario.id,
                tipo_saida=item["tipo_saida"],
            )

            session.add(saida)
        else:
            diferenca: ColumnElement[Decimal] = quantidade - saida.quantidade

            if diferenca > 0:
                if diferenca > estoque.quantidade_atual:
                    raise RuntimeError(f"Saldo insuficiente ao sincronizar saída de {item["entrada_code"]}.")

                estoque.quantidade_atual -= diferenca
            elif diferenca < 0:
                estoque.quantidade_atual += abs(diferenca.value)

            saida.data_saida = data_saida
            saida.quantidade = quantidade
            saida.preco_venda_unitario = preco

        await session.flush()