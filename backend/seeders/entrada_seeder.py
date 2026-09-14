from sqlalchemy.engine.result import Result
from sqlalchemy.sql.selectable import Select
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from seeders.bootstrap import SRC_DIR  # noqa: F401
from models.entrada_model import EntradaModel
from models.estoque_model import EstoqueModel
from models.fornecedor_model import FornecedorModel
from models.lote_model import LoteModel
from models.usuario_model import UsuarioModel

def _entry_specs() -> list[dict]:
    specs: list[dict] = []

    tipos: list[str] = [
        "COMPRA",
        "COMPRA",
        "COMPRA",
        "DEVOLUCAO",
        "AJUSTE",
    ]

    extra_products: dict[int, tuple[int, str]] = {
        31: (6, "B"),
        32: (8, "B"),
        33: (9, "B"),
        34: (10, "B"),
        35: (13, "B"),
        36: (21, "A"),
        37: (22, "A"),
        38: (23, "A"),
        39: (24, "A"),
        40: (25, "A"),
    }

    for index in range(1, 41):
        if index <= 30:
            product_index: int = index
            lote_suffix = "A"
        else:
            product_index, lote_suffix = extra_products[index]

        specs.append(
            {
                "code": f"E{index:03d}",
                "produto_codigo": f"SEED-PROD-{product_index:03d}",
                "lote_numero": f"LT-{product_index:03d}-{lote_suffix}",
                "fornecedor_index": ((index - 1) % 12) + 1,
                "usuario_index": ((index - 1) % 12) + 1,
                "quantidade": Decimal(str(25 + (index % 6) * 10)),
                "preco_custo_unitario": Decimal(str(round(2.50 + index * 0.73, 2))),
                "tipo_entrada": tipos[(index - 1) % len(tipos)],
                "days_ago": 90 - index,
                "corredor": f"C{((index - 1) % 5) + 1}",
                "prateleira": f"P{((index - 1) % 4) + 1}",
                "secao": f"S{((index - 1) % 6) + 1}",
            }
        )

    specs[2]["quantidade"] = Decimal("20.000")
    specs[5]["quantidade"] = Decimal("30.000")
    specs[6]["quantidade"] = Decimal("12.000")
    specs[11]["quantidade"] = Decimal("25.000")

    return specs

async def seed_entradas(
    session: AsyncSession,
    lotes: dict[str, LoteModel],
    fornecedores: dict[str, FornecedorModel],
    usuarios: dict[str, UsuarioModel],
) -> dict[str, EstoqueModel]:
    print("Seeding entradas e estoques...")

    fornecedor_list: list[FornecedorModel] = list(fornecedores.values())
    usuario_list: list[UsuarioModel] = list(usuarios.values())

    if not fornecedor_list or not usuario_list:
        raise RuntimeError("Fornecedores e usuários devem existir antes das entradas.")

    result: dict[str, EstoqueModel] = {}

    now: datetime = datetime.now().replace(
        hour=9,
        minute=0,
        second=0,
        microsecond=0,
    )

    for item in _entry_specs():
        marker: str = f'[SEED: {item["code"]}]'

        query: Select[tuple[EntradaModel]] = select(EntradaModel).where(EntradaModel.observacao.like(f"{marker}%"))

        query_result: Result[tuple[EntradaModel]] = await session.execute(query)
        entrada: EntradaModel | None = query_result.scalar_one_or_none()

        lote_key: str = f'{item["produto_codigo"]}: {item["lote_numero"]}'
        lote: LoteModel = lotes[lote_key]

        fornecedor: FornecedorModel = fornecedor_list[item["fornecedor_index"] - 1]
        usuario: UsuarioModel = usuario_list[item["usuario_index"] - 1]

        data_entrada: datetime = now - timedelta(days=item["days_ago"])
        observacao: str = f"{marker} Entrada gerada para testes de paginação, filtros e histórico."

        if entrada is None:
            entrada = EntradaModel(
                data_entrada=data_entrada,
                quantidade=item["quantidade"],
                preco_custo_unitario=item["preco_custo_unitario"],
                tipo_entrada=item["tipo_entrada"],
                observacao=observacao,
                fornecedor_id=fornecedor.id,
                lote_id=lote.id,
                usuario_id=usuario.id,
            )

            session.add(entrada)
            await session.flush()
        else:
            entrada.data_entrada = data_entrada
            entrada.preco_custo_unitario = item["preco_custo_unitario"]
            entrada.tipo_entrada = item["tipo_entrada"]
            entrada.observacao = observacao
            entrada.fornecedor_id = fornecedor.id
            entrada.lote_id = lote.id
            entrada.usuario_id = usuario.id

            await session.flush()

        estoque_query: Select[tuple[EstoqueModel]] = select(EstoqueModel).where(EstoqueModel.entrada_id == entrada.id)
        estoque_result: Result[tuple[EstoqueModel]] = await session.execute(estoque_query)

        estoque: EstoqueModel | None = estoque_result.scalar_one_or_none()

        if estoque is None:
            estoque = EstoqueModel(
                entrada_id=entrada.id,
                quantidade_atual=item["quantidade"],
                corredor=item["corredor"],
                prateleira=item["prateleira"],
                secao=item["secao"],
            )

            session.add(estoque)
            await session.flush()
        else:
            estoque.corredor = item["corredor"]
            estoque.prateleira = item["prateleira"]
            estoque.secao = item["secao"]

            await session.flush()

        result[item["code"]] = estoque

    return result