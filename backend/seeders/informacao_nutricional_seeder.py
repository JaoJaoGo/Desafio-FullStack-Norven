from sqlalchemy.engine.result import Result
from sqlalchemy.sql.selectable import Select
from decimal import Decimal
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from seeders.bootstrap import SRC_DIR  # noqa: F401
from models.informacao_nutricional_model import InformacaoNutricionalModel
from models.unidade_medida_model import UnidadeMedidaModel

NUTRICOES = {
    "NUT-001": (Decimal("50.00"), Decimal("180.00"), Decimal("40.00"), Decimal("4.00"), Decimal("0.50"), "Arroz beneficiado tipo 1.", None, "g"),
    "NUT-002": (Decimal("60.00"), Decimal("205.00"), Decimal("36.00"), Decimal("12.00"), Decimal("1.20"), "Feijão carioca.", None, "g"),
    "NUT-003": (Decimal("80.00"), Decimal("286.00"), Decimal("58.00"), Decimal("9.00"), Decimal("1.50"), "Sêmola de trigo e água.", "Contém trigo e glúten.", "g"),
    "NUT-004": (Decimal("5.00"), Decimal("20.00"), Decimal("5.00"), Decimal("0.00"), Decimal("0.00"), "Açúcar cristal.", None, "g"),
    "NUT-005": (Decimal("10.00"), Decimal("25.00"), Decimal("4.00"), Decimal("1.50"), Decimal("0.60"), "Café torrado e moído.", None, "g"),
    "NUT-006": (Decimal("200.00"), Decimal("124.00"), Decimal("9.40"), Decimal("6.40"), Decimal("6.60"), "Leite integral.", "Contém leite e derivados.", "mL"),
    "NUT-007": (Decimal("170.00"), Decimal("110.00"), Decimal("12.00"), Decimal("6.00"), Decimal("4.20"), "Leite e fermento lácteo.", "Contém leite e derivados.", "g"),
    "NUT-008": (Decimal("30.00"), Decimal("96.00"), Decimal("0.80"), Decimal("7.00"), Decimal("7.20"), "Leite, sal e fermento.", "Contém leite e derivados.", "g"),
    "NUT-009": (Decimal("200.00"), Decimal("84.00"), Decimal("21.00"), Decimal("0.00"), Decimal("0.00"), "Água gaseificada, açúcar e aromatizantes.", None, "mL"),
    "NUT-010": (Decimal("200.00"), Decimal("90.00"), Decimal("22.00"), Decimal("1.00"), Decimal("0.20"), "Suco de laranja integral.", None, "mL"),
    "NUT-011": (Decimal("100.00"), Decimal("219.00"), Decimal("0.00"), Decimal("35.00"), Decimal("8.00"), "Carne bovina.", None, "g"),
    "NUT-012": (Decimal("100.00"), Decimal("165.00"), Decimal("0.00"), Decimal("31.00"), Decimal("3.60"), "Peito de frango.", None, "g"),
    "NUT-013": (Decimal("100.00"), Decimal("296.00"), Decimal("1.00"), Decimal("16.00"), Decimal("25.00"), "Carne suína, sal e especiarias.", None, "g"),
    "NUT-014": (Decimal("100.00"), Decimal("98.00"), Decimal("26.00"), Decimal("1.30"), Decimal("0.30"), "Banana prata.", None, "g"),
    "NUT-015": (Decimal("100.00"), Decimal("56.00"), Decimal("15.00"), Decimal("0.30"), Decimal("0.20"), "Maçã gala.", None, "g"),
    "NUT-016": (Decimal("50.00"), Decimal("135.00"), Decimal("28.00"), Decimal("4.00"), Decimal("1.20"), "Farinha de trigo, água, fermento e sal.", "Contém trigo e glúten.", "g"),
    "NUT-017": (Decimal("50.00"), Decimal("128.00"), Decimal("24.00"), Decimal("4.50"), Decimal("1.50"), "Farinha de trigo, água e fermento.", "Contém trigo e glúten.", "g"),
    "NUT-018": (Decimal("80.00"), Decimal("210.00"), Decimal("28.00"), Decimal("8.00"), Decimal("7.00"), "Farinha, queijo, molho e cobertura.", "Contém trigo, glúten e leite.", "g"),
    "NUT-019": (Decimal("30.00"), Decimal("132.00"), Decimal("21.00"), Decimal("2.80"), Decimal("4.20"), "Farinha de trigo, gordura vegetal e sal.", "Contém trigo e glúten.", "g"),
    "NUT-020": (Decimal("13.00"), Decimal("108.00"), Decimal("0.00"), Decimal("0.00"), Decimal("12.00"), "Óleo de soja.", "Contém derivados de soja.", "mL"),
}

async def seed_informacoes_nutricionais(session: AsyncSession, unidades: dict[str, UnidadeMedidaModel]) -> dict[str, InformacaoNutricionalModel]:
    print("Seeding informações nutricionais...")

    result: dict[str, InformacaoNutricionalModel] = {}

    for key, item in NUTRICOES.items():
        (
            porcao,
            kcal,
            carboidratos,
            proteinas,
            gorduras,
            ingredientes,
            alergenicos,
            unidade_sigla,
        ) = item

        unidade: UnidadeMedidaModel = unidades[unidade_sigla]

        query: Select[tuple[InformacaoNutricionalModel]] = select(InformacaoNutricionalModel).where(
            and_(
                InformacaoNutricionalModel.porcao_quantidade == porcao,
                InformacaoNutricionalModel.ingredientes == ingredientes,
                InformacaoNutricionalModel.unidade_porcao_id == unidade.id,
            )
        )

        query_result: Result[tuple[InformacaoNutricionalModel]] = await session.execute(query)
        info: InformacaoNutricionalModel | None = query_result.scalar_one_or_none()

        if info is None:
            info = InformacaoNutricionalModel(
                porcao_quantidade=porcao,
                valor_energetico_kcal=kcal,
                carboidratos_g=carboidratos,
                proteinas_g=proteinas,
                gorduras_totais_g=gorduras,
                ingredientes=ingredientes,
                alergenicos=alergenicos,
                unidade_porcao_id=unidade.id,
            )

            session.add(info)
        else:
            info.valor_energetico_kcal = kcal
            info.carboidratos_g = carboidratos
            info.proteinas_g = proteinas
            info.gorduras_totais_g = gorduras
            info.alergenicos = alergenicos

        await session.flush()
        result[key] = info

    return result
