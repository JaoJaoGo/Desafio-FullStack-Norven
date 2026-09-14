from sqlalchemy.engine.result import Result
from sqlalchemy.sql.selectable import Select
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from seeders.bootstrap import SRC_DIR  # noqa: F401
from core.configs import settings
from models.lote_model import LoteModel
from models.produto_model import ProdutoModel

def _expiry_dates() -> dict[str, date]:
    today: date = date.today()

    alert_days: int = max(1, settings.PRODUTO_VALIDADE_ALERTA_DIAS)

    near_days: int = max(1, min(7, alert_days))

    return {
        "expired": today - timedelta(days=10),
        "expired_old": today - timedelta(days=45),
        "near": today + timedelta(days=near_days),
        "near_2": today + timedelta(days=alert_days),
        "future": today + timedelta(days=alert_days + 60),
        "future_2": today + timedelta(days=alert_days + 120),
    }

def _build_lote_specs(produtos: dict[str, ProdutoModel]) -> list[dict]:
    dates: dict[str, date] = _expiry_dates()
    specs: list[dict] = []

    for index in range(1, 31):
        codigo: str = f"SEED-PROD-{index:03d}"
        produto: ProdutoModel = produtos[codigo]

        expiry: date | None = (
            dates["future"]
            if produto.eh_perecivel
            else None
        )

        if codigo == "SEED-PROD-006":
            expiry = dates["expired"]
        elif codigo == "SEED-PROD-007":
            expiry = dates["near"]
        elif codigo == "SEED-PROD-012":
            expiry = dates["expired_old"]
        elif codigo == "SEED-PROD-015":
            expiry = dates["near"]

        specs.append(
            {
                "produto_codigo": codigo,
                "numero": f"LT-{index:03d}-A",
                "data_validade": expiry,
            }
        )

    for index in range(6, 16):
        codigo: str = f"SEED-PROD-{index:03d}"
        produto: ProdutoModel = produtos[codigo]

        expiry: date | None = dates["future_2"] if produto.eh_perecivel else None

        specs.append(
            {
                "produto_codigo": codigo,
                "numero": f"LT-{index:03d}-B",
                "data_validade": expiry,
            }
        )

    return specs

async def seed_lotes(session: AsyncSession, produtos: dict[str, ProdutoModel]) -> dict[str, LoteModel]:
    print("Seeding lotes...")

    result: dict[str, LoteModel] = {}

    for item in _build_lote_specs(produtos):
        produto: ProdutoModel = produtos[item["produto_codigo"]]

        query: Select[tuple[LoteModel]] = select(LoteModel).where(LoteModel.produto_id == produto.id, LoteModel.numero == item["numero"])

        query_result: Result[tuple[LoteModel]] = await session.execute(query)
        lote: LoteModel | None = query_result.scalar_one_or_none()

        if lote is None:
            lote = LoteModel(
                numero=item["numero"],
                data_validade=item["data_validade"],
                produto_id=produto.id,
            )

            session.add(lote)
        else:
            lote.data_validade = item["data_validade"]

        await session.flush()

        result[f'{item["produto_codigo"]}: {item["numero"]}'] = lote

    return result
