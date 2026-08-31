from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.lote_repository import LoteRepository
from repositories.produto_repository import ProdutoRepository
from schemas.lote_schema import LoteCreateSchema, LoteFilterSchema, LoteResponseSchema, LoteUpdateSchema

class LoteService:
    @staticmethod
    async def validate_create(db: AsyncSession, data: LoteCreateSchema) -> None:
        produto = await ProdutoRepository.find_by_id(db, data.produto_id)

        if produto is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado.")

        if produto.eh_perecivel and data.data_validade is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Data de validade é obrigatória para produtos perecíveis.")

        lote_existente = await LoteRepository.find_by_product_and_number(db, data.produto_id, data.numero)

        if lote_existente is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um lote com este número para este produto.")

    @staticmethod
    async def create(db: AsyncSession, data: LoteCreateSchema, commit: bool = True):
        try:
            await LoteService.validate_create(db, data)

            lote = await LoteRepository.create(db, data)

            if commit:
                await db.commit()

                return await LoteService.find_by_id(db, lote.id)
            
            return lote
        except HTTPException:
            if commit:
                await db.rollback()

            raise
        except IntegrityError:
            if commit:
                await db.rollback()

            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível cadastrar o lote.")
        except Exception:
            if commit:
                await db.rollback()

            raise

    @staticmethod
    async def find_by_id(db: AsyncSession, lote_id: int) -> LoteResponseSchema:
        row = await LoteRepository.find_detail_by_id(db, lote_id)

        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote não encontrado.")

        return LoteResponseSchema(**row)

    @staticmethod
    async def list(db: AsyncSession, filters: LoteFilterSchema) -> List[LoteResponseSchema]:
        rows, total = await LoteRepository.list(db, filters)

        items = [LoteResponseSchema(**row) for row in rows]
        
        return items, total

    @staticmethod
    async def list_by_product(db: AsyncSession, produto_id: int) -> List[LoteResponseSchema]:
        rows = await LoteRepository.list_by_product(db, produto_id)
        
        return [LoteResponseSchema(**row) for row in rows]

    @staticmethod
    async def update(db: AsyncSession, lote_id: int, data: LoteUpdateSchema):
        lote = await LoteRepository.find_by_id(db, lote_id)

        if lote is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote não encontrado.")

            try:
                values = data.model_dump(exclude_unset=True)

                if data.numero is not None and data.numero != lote.numero:
                    existente = await LoteRepository.find_by_product_and_number(db, lote.produto_id, data.numero)

                    if existente is not None and existente.id != lote.id:
                        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um lote com este número para este produto.")

                if values:
                    await LoteRepository.update(db, lote_id, values)

                await db.commit()

                return await LoteService.find_by_id(db, lote_id)
            except HTTPException:
                await db.rollback()
                raise
            except IntegrityError:
                await db.rollback()

                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar o lote.")
            except Exception:
                await db.rollback()
                raise