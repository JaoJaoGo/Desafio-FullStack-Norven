from sqlalchemy.engine.result import Result
from sqlalchemy.sql.selectable import Select
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from seeders.bootstrap import SRC_DIR  # noqa: F401
from models.unidade_medida_model import UnidadeMedidaModel

UNIDADES: list[tuple[str, str]] = [
    ("Unidade", "un"),
    ("Quilograma", "kg"),
    ("Grama", "g"),
    ("Litro", "L"),
    ("Mililitro", "mL"),
    ("Caixa", "cx"),
    ("Pacote", "pct"),
    ("Dúzia", "dz"),
    ("Bandeja", "bdj"),
    ("Metro", "m"),
]


async def seed_unidades_medidas(session: AsyncSession) -> dict[str, UnidadeMedidaModel]:
    print("Seeding unidades de medida...")

    result: dict[str, UnidadeMedidaModel] = {}

    for nome, sigla in UNIDADES:
        query: Select[tuple[UnidadeMedidaModel]] = select(UnidadeMedidaModel).where(
            or_(
                UnidadeMedidaModel.nome == nome,
                UnidadeMedidaModel.sigla == sigla,
            )
        )

        query_result: Result[tuple[UnidadeMedidaModel]] = await session.execute(query)
        unidade: UnidadeMedidaModel | None = query_result.scalar_one_or_none()

        if unidade is None:
            unidade = UnidadeMedidaModel(nome=nome, sigla=sigla)
            
            session.add(unidade)
            await session.flush()
        else:
            unidade.nome = nome
            unidade.sigla = sigla

        result[sigla] = unidade

    return result
