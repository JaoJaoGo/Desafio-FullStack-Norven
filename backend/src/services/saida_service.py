from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import TipoSaidaEnum
from models.usuario_model import UsuarioModel
from repositories.estoque_repository import EstoqueRepository
from repositories.saida_repository import SaidaRepository
from schemas.saida_schema import SaidaFilterSchema, SaidaResponseSchema, SaidaUpdateSchema

class SaidaService:
    @staticmethod
    async def create(db: AsyncSession, *, produto_id: int, data, current_user: UsuarioModel) -> SaidaResponseSchema:
        try:
            estoque = await EstoqueRepository.lock_by_id(db, data.estoque_id)

            if estoque is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estoque não encontrado.")

            contexto = await EstoqueRepository.get_context(db, estoque.id)

            if contexto is None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível localizar o produto do estoque.")

            if contexto["produto_id"] != produto_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="O estoque selecionado não pertence ao produto.")

            if data.quantidade > estoque.quantidade_atual:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Estoque insuficiente. Disponível: {estoque.quantidade_atual}.")

            if data.data_saida is not None and data.data_saida < contexto["data_entrada"]:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="A saída não pode ocorrer antes da entrada.")

            if data.tipo_saida == TipoSaidaEnum.VENDA:
                preco = data.preco_venda_unitario

                if preco is None:
                    preco = contexto["preco_venda_atual"]

            else:
                if data.preco_venda_unitario is not None:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Somente saídas do tipo VENDA podem possuir preço.")

                preco = None

            values = {
                "quantidade": data.quantidade,
                "tipo_saida": data.tipo_saida,
                "preco_venda_unitario": preco,
                "estoque_id": estoque.id,
                "usuario_id": current_user.id
            }

            if data.data_saida is not None:
                values["data_saida"] = data.data_saida

            estoque.quantidade_atual -= data.quantidade

            saida = await SaidaRepository.create(db, **values)

            await db.flush()
            await db.commit()

            return await SaidaService.find_by_id(db, saida.id)
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()

            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível registrar a saída.")
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def find_by_id(db: AsyncSession, saida_id: int) -> SaidaResponseSchema:
        row = await SaidaRepository.find_detail_by_id(db, saida_id)

        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saída não encontrada.")

        return SaidaResponseSchema(**row)

    @staticmethod
    async def list(db: AsyncSession, filters: SaidaFilterSchema) -> tuple[list[SaidaResponseSchema], int]:
        rows, total = await SaidaRepository.list(db, filters)

        items = [SaidaResponseSchema(**row) for row in rows]

        return items, total

    @staticmethod
    async def update(db: AsyncSession, saida_id: int, data: SaidaUpdateSchema) -> SaidaResponseSchema:
        saida = await SaidaRepository.find_by_id(db, saida_id)

        if saida is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saída não encontrada.")

        try:
            estoque = await EstoqueRepository.lock_by_id(db, saida.estoque_id)

            if estoque is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estoque não encontrado.")

            contexto = (await EstoqueRepository.get_context(db, estoque.id))

            if contexto is None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível localizar o produto da saída.")

            nova_quantidade = (data.quantidade if data.quantidade is not None else saida.quantidade)

            diferenca = (nova_quantidade - saida.quantidade)

            if diferenca > 0:
                if (diferenca > estoque.quantidade_atual):
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Estoque insuficiente para aumentar a saída.")

                estoque.quantidade_atual -= diferenca

            elif diferenca < 0:
                estoque.quantidade_atual += abs(diferenca)

            tipo_final = (data.tipo_saida if data.tipo_saida is not None else saida.tipo_saida)

            data_final = (data.data_saida if data.data_saida is not None else saida.data_saida)

            if data_final < contexto["data_entrada"]:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="A saída não pode ocorrer antes da entrada.")

            if tipo_final == TipoSaidaEnum.VENDA:
                if ("preco_venda_unitario" in data.model_fields_set):
                    preco_final = data.preco_venda_unitario

                    if preco_final is None:
                        preco_final = contexto["preco_venda_atual"]

                elif (saida.tipo_saida == TipoSaidaEnum.VENDA and saida.preco_venda_unitario is not None):
                    preco_final = saida.preco_venda_unitario

                else:
                    preco_final = contexto["preco_venda_atual"]

            else:
                if ("preco_venda_unitario" in data.model_fields_set and data.preco_venda_unitario is not None):
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Somente saídas do tipo VENDA podem possuir preço.")

                preco_final = None

            values = {
                "quantidade": nova_quantidade,
                "tipo_saida": tipo_final,
                "preco_venda_unitario": preco_final,
                "data_saida": data_final
            }

            await SaidaRepository.update(db=db, saida=saida, values=values)

            await db.flush()
            await db.commit()

            return await SaidaService.find_by_id(db, saida.id)
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()

            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar a saída.")
        except Exception:
            await db.rollback()
            raise