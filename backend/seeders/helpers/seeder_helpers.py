from sqlalchemy.engine.result import Result
from sqlalchemy.sql.selectable import Select
from collections.abc import Iterable
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.cidade_model import CidadeModel
from models.estado_model import EstadoModel

def to_decimal(value: int | float | str | Decimal) -> Decimal:
    return Decimal(str(value))

async def find_city_id(session: AsyncSession, city_name: str, uf: str) -> int:
    query: Select[tuple[int]] = (
        select(CidadeModel.id)
        .join(EstadoModel, CidadeModel.estado_id == EstadoModel.id)
        .where(CidadeModel.nome == city_name, EstadoModel.uf == uf)
    )

    result: Result[tuple[int]] = await session.execute(query)
    city_id: int | None = result.scalar_one_or_none()

    if city_id is not None:
        return city_id

    fallback_query: Select[tuple[int]] = (
        select(CidadeModel.id)
        .join(EstadoModel, CidadeModel.estado_id == EstadoModel.id)
        .where(CidadeModel.nome == "Goiânia", EstadoModel.uf == "GO")
    )

    fallback_result: Result[tuple[int]] = await session.execute(fallback_query)
    fallback_id: int | None = fallback_result.scalar_one_or_none()

    if fallback_id is None:
        raise RuntimeError("Goiânia/GO não foi encontrada. Execute o GeographySeeder antes dos seeders da aplicação.")

    return fallback_id

async def get_city_map(session: AsyncSession, cities: Iterable[tuple[str, str]]) -> dict[tuple[str, str], int]:
    result: dict[tuple[str, str], int] = {}

    for city_name, uf in cities:
        result[(city_name, uf)] = await find_city_id(session, city_name, uf)

    return result