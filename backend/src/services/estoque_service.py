from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.estoque_repository import EstoqueRepository
from schemas.estoque_schema import EstoqueFilterSchema, EstoqueResponseSchema, EstoqueUpdateSchema

class EstoqueService:
    @staticmethod
    async def find_by_id(db: AsyncSession, estoque_id: int) -> EstoqueResponseSchema:
        row = await EstoqueRepository.find_detail_by_id(db, estoque_id)

        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estoque não encontrado")

        return EstoqueResponseSchema(**row)

    @staticmethod
    async def list(db: AsyncSession, filters: EstoqueFilterSchema) -> tuple[list[EstoqueResponseSchema], int]:
        rows, total = await EstoqueRepository.list(
            db=db,
            search=filters.search,
            produto_id=filters.produto_id,
            lote_id=filters.lote_id,
            somente_com_saldo=filters.somente_com_saldo,
            page=filters.page,
            per_page=filters.per_page
        )

        items = [EstoqueResponseSchema(**row) for row in rows]

        return items, total

    @staticmethod
    async def list_by_product(db: AsyncSession, produto_id: int) -> list[EstoqueResponseSchema]:
        rows = await EstoqueRepository.list_by_product(db, produto_id)

        return [EstoqueResponseSchema(**row) for row in rows]

    @staticmethod
    async def update(db: AsyncSession, estoque_id: int, data: EstoqueUpdateSchema) -> EstoqueResponseSchema:
        estoque = await EstoqueRepository.find_by_id(db, estoque_id)

        if estoque is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estoque não encontrado.")

        try:
            values = data.model_dump(exclude_unset=True)

            localizacao = values.pop("localizacao", None)

            if localizacao is not None:
                values.update(localizacao)

            if values:
                await EstoqueRepository.update(db=db, estoque=estoque, values=values)

            await db.commit()

            return await EstoqueService.find_by_id(db, estoque_id)
        except HTTPException:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise