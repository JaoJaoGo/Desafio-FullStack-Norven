from typing import Optional
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.unidade_medida_model import UnidadeMedidaModel

class UnidadeMedidaRepository:
    @staticmethod
    async def find_by_id(db: AsyncSession, unidade_medida_id: int) -> Optional[UnidadeMedidaModel]:
        query = select(UnidadeMedidaModel).filter(UnidadeMedidaModel.id == unidade_medida_id)
        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def find_by_name(db: AsyncSession, nome: str) -> Optional[UnidadeMedidaModel]:
        query = select(UnidadeMedidaModel).where(UnidadeMedidaModel.nome == nome)

        result = await db.execute(query)

        return result.scalars().unique().one_or_none()

    @staticmethod
    async def find_by_sigla(db: AsyncSession, sigla: str) -> Optional[UnidadeMedidaModel]:
        query = select(UnidadeMedidaModel).where(UnidadeMedidaModel.sigla == sigla)

        result = await db.execute(query)

        return result.scalars().unique().one_or_none()


    @staticmethod
    async def list(db: AsyncSession, search: Optional[str], page: int, per_page: int) -> tuple[list[UnidadeMedidaModel], int]:
        conditions = []

        if search:
            search_value = f"%{search.strip()}%"

            conditions.append(
                or_(
                    UnidadeMedidaModel.nome.ilike(search_value),
                    UnidadeMedidaModel.sigla.ilike(search_value)
                )
            )

        # TOTAL
        count_query = select(func.count(UnidadeMedidaModel.id))

        if conditions:
            count_query = count_query.where(*conditions)

        count_result = await db.execute(count_query)

        total = count_result.scalar_one()

        # REGISTROS
        query = select(UnidadeMedidaModel)

        if conditions:
            query = query.where(*conditions)

        query = (
            query.order_by(UnidadeMedidaModel.nome.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        result = await db.execute(query)

        unidades = list(result.scalars().all())

        return unidades, total

    @staticmethod
    async def create(db: AsyncSession, nome: str, sigla: str) -> UnidadeMedidaModel:
        unidade = UnidadeMedidaModel(nome=nome, sigla=sigla)

        db.add(unidade)
        await db.flush()

        return unidade


    @staticmethod
    async def update(db: AsyncSession, unidade: UnidadeMedidaModel, values: dict) -> UnidadeMedidaModel:
        for field, value in values.items():
            setattr(unidade, field, value)

        await db.flush()

        return unidade