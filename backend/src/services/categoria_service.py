from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.categoria_model import CategoriaModel
from repositories.categoria_repository import CategoriaRepository
from schemas.categoria_schema import CategoriaCreateSchema, CategoriaUpdateSchema

class CategoriaService:
    @staticmethod
    async def create(db: AsyncSession, data: CategoriaCreateSchema) -> CategoriaModel:
        try:
            existente = await CategoriaRepository.find_by_name(db, data.nome)

            if existente is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe uma categoria com este nome.")

            categoria = await CategoriaRepository.create(db=db, nome=data.nome)

            await db.commit()
            await db.refresh(categoria)

            return categoria
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()

            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível cadastrar a categoria.")

    @staticmethod
    async def list(db: AsyncSession, search: Optional[str], page: int, per_page: int) -> tuple[list[CategoriaModel], int]:
        return await CategoriaRepository.list(db, search, page, per_page)

    @staticmethod
    async def find_by_id(db: AsyncSession, categoria_id: int) -> CategoriaModel:
        categoria = await CategoriaRepository.find_by_id(db, categoria_id)

        if categoria is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")

        return categoria

    @staticmethod
    async def update(db: AsyncSession, categoria_id: int, data: CategoriaUpdateSchema) -> CategoriaModel:
        categoria = await CategoriaService.find_by_id(db, categoria_id)

        try:
            values = data.model_dump(exclude_unset=True)

            if data.nome is not None and data.nome != categoria.nome:
                existente = await CategoriaRepository.find_by_name(db, data.nome)

                if existente is not None and existente.id != categoria.id:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe uma categoria com este nome.")

            if values:
                await CategoriaRepository.update(db, categoria, values)

            await db.commit()
            await db.refresh(categoria)

            return categoria
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()

            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar a categoria.")