from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.unidade_medida_model import UnidadeMedidaModel
from repositories.unidade_medida_repository import UnidadeMedidaRepository
from schemas.unidade_medida_schema import UnidadeMedidaCreateSchema, UnidadeMedidaUpdateSchema

class UnidadeMedidaService:
    @staticmethod
    async def create(db: AsyncSession, data: UnidadeMedidaCreateSchema) -> UnidadeMedidaModel:
        try:
            existente_nome = await UnidadeMedidaRepository.find_by_name(db, data.nome)

            if existente_nome is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe uma unidade de medida com este nome.")

            existente_sigla = await UnidadeMedidaRepository.find_by_sigla(db, data.sigla)

            if existente_sigla is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe uma unidade de medida com esta sigla.")

            unidade = await UnidadeMedidaRepository.create(db, data.nome, data.sigla)

            await db.commit()
            await db.refresh(unidade)

            return unidade
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()

            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível cadastrar a unidade de medida.")

    @staticmethod
    async def list(db: AsyncSession, search: Optional[str], page: int, per_page: int) -> tuple[list[UnidadeMedidaModel], int]:
        return await UnidadeMedidaRepository.list(db=db, search=search, page=page, per_page=per_page)

    @staticmethod
    async def find_by_id(db: AsyncSession, unidade_id: int) -> UnidadeMedidaModel:
        unidade = await UnidadeMedidaRepository.find_by_id(db, unidade_id)

        if unidade is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade de medida não encontrada.")

        return unidade

    @staticmethod
    async def update(db: AsyncSession, unidade_id: int, data: UnidadeMedidaUpdateSchema) -> UnidadeMedidaModel:
        unidade = await UnidadeMedidaService.find_by_id(db, unidade_id)

        try:
            values = data.model_dump(exclude_unset=True)

            # Nome
            if data.nome is not None and data.nome != unidade.nome:
                existente = await UnidadeMedidaRepository.find_by_name(db, data.nome)

                if existente is not None and existente.id != unidade.id:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe uma unidade de medida com este nome.")

            # Sigla
            if data.sigla is not None and data.sigla != unidade.sigla:
                existente = await UnidadeMedidaRepository.find_by_sigla(db, data.sigla)

                if existente is not None and existente.id != unidade.id:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe uma unidade de medida com esta sigla.")

            if values:
                await UnidadeMedidaRepository.update(db, unidade, values)

            await db.commit()
            await db.refresh(unidade)

            return unidade
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()

            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar a unidade de medida.")