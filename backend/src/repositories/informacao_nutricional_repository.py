from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.informacao_nutricional_model import InformacaoNutricionalModel
from schemas.informacao_nutricional_schema import InformacaoNutricionalCreateSchema

class InformacaoNutricionalRepository:
    @staticmethod
    async def find_by_data(db: AsyncSession, data: InformacaoNutricionalCreateSchema) -> Optional[InformacaoNutricionalModel]:
        query = select(InformacaoNutricionalModel).where(
            InformacaoNutricionalModel.porcao_quantidade == data.porcao_quantidade,
            InformacaoNutricionalModel.valor_energetico_kcal == data.valor_energetico_kcal,
            InformacaoNutricionalModel.carboidratos_g == data.carboidratos_g,
            InformacaoNutricionalModel.proteinas_g == data.proteinas_g,
            InformacaoNutricionalModel.gorduras_totais_g == data.gorduras_totais_g,
            InformacaoNutricionalModel.ingredientes == data.ingredientes,
            InformacaoNutricionalModel.alergenicos == data.alergenicos,
            InformacaoNutricionalModel.unidade_porcao_id == data.unidade_porcao_id,
        )
        result = await db.execute(query)

        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: InformacaoNutricionalCreateSchema) -> InformacaoNutricionalModel:
        informacao = InformacaoNutricionalModel(**data.model_dump())

        db.add(informacao)
        await db.flush()

        return informacao