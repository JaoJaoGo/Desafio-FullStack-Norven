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
        rows, total = await EstoqueRepository.list(db, filters)

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

            if values:
                await EstoqueRepository.update(db, estoque, values)

            await db.commit()

            return await EstoqueService.find_by_id(db, estoque_id)
        except HTTPException:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise