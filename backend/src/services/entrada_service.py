from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.usuario_model import UsuarioModel
from repositories.entrada_repository import EntradaRepository
from repositories.estoque_repository import EstoqueRepository
from repositories.fornecedor_repository import FornecedorRepository
from repositories.lote_repository import LoteRepository
from repositories.produto_repository import ProdutoRepository
from schemas.entrada_schema import EntradaFilterSchema, EntradaResponseSchema, EntradaUpdateSchema
from schemas.lote_schema import LoteCreateSchema
from services.lote_service import LoteService

class EntradaService:
    @staticmethod
    async def _resolve_lote(db: AsyncSession, produto, lote_id, novo_lote):
        if lote_id is not None:
            lote = await LoteRepository.find_by_id(db, lote_id)

            if lote is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote não encontrado.")
            
            if lote.produto_id != produto.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Lote não pertence ao produto.")

            return lote

        lote_data = LoteCreateSchema(
            produto_id=produto.id,
            numero=novo_lote.numero,
            data_validade=novo_lote.data_validade
        )

        return await LoteService.create(db=db, data=lote_data, commit=False)

    @staticmethod
    async def create(db: AsyncSession, *, produto_id: int, data, current_user: UsuarioModel) -> EntradaResponseSchema:
        try:
            produto = await ProdutoRepository.find_by_id(db, produto_id)

            if produto is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado.")

            fornecedor = await FornecedorRepository.find_by_id(db, data.fornecedor_id)

            if fornecedor is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor não encontrado.")

            lote = await EntradaService._resolve_lote(db, produto, lote_id, novo_lote)

            values = {
                "quantidade": data.quantidade,
                "preco_custo_unitario": data.preco_custo_unitario,
                "tipo_entrada": data.tipo_entrada.strip().upper(),
                "observacao": data.observacao,
                "fornecedor_id": fornecedor.id,
                "lote_id": lote.id,
                "usuario_id": current_user.id,
            }        

            if data.data_entrada is not None:
                values["data_entrada"] = data.data_entrada
            
            entrada = await EntradaRepository.create(db, **values)

            await EstoqueRepository.create(
                db,
                entrada_id=entrada.id,
                quantidade=data.quantidade,
                corredor=data.localizacao.corredot,
                prateleira=data.localizacao.prateleira,
                secao=data.localizacao.secao
            )

            await db.commit()

            return await EntradaService.find_by_id(db, entrada.id)
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()

            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível registrar a entrada.")
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def find_by_id(db: AsyncSession, entrada_id: int) -> EntradaResponseSchema:
        row = await EntradaRepository.find_detail_by_id(db, entrada_id)

        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrada não encontrada.")

        return EntradaResponseSchema(**row)

    @staticmethod
    async def list(db: AsyncSession, filters: EntradaFilterSchema) -> tuple[list[EntradaResponseSchema], int]:
        rows, total = await EntradaRepository.list(db, filters)

        items = [EntradaResponseSchema(**row) for row in rows]

        return items, total

    @staticmethod
    async def update(db: AsyncSession, entrada_id: int, data: EntradaUpdateSchema) -> EntradaResponseSchema:
        entrada = await EntradaRepository.find_by_id(db, entrada_id)

        if entrada is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrada não encontrada.")

        try:
            estoque = await EstoqueRepository.lock_by_entry(db, entrada.id)

            if estoque is None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A entrada não possui estoque associado.")

            values = {}

            if data.quantidade is not None:
                consumido = entrada.quantidade - estoque.quantidade_atual

                if data.quantidade < consumido:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A quantidade da entrada é inferior ao total já retirado do estoque.")

                estoque.quantidade_atual = data.quantidade - consumido

                values["quantidade"] = data.quantidade

            if data.fornecedor_id is not None:
                fornecedor = await FornecedorRepository.find_by_id(db, data.fornecedor_id)

                if fornecedor is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor não encontrado.")

                values["fornecedor_id"] = fornecedor.id
            
            if data.preco_custo_unitario is not None:
                values["preco_custo_unitario"] = data.preco_custo_unitario

            if data.tipo_entrada is not None:
                values["tipo_entrada"] = data.tipo_entrada.strip().upper()

            if "observacao" in data.model_fields_set:
                values['observacao'] = data.observacao

            if data.data_entrada is not None:
                primeira_data = await EntradaRepository.get_first_exit_date(db, entrada.id)

                if primeira_data is not None and data.data_entrada > primeira_data:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A data de entrada não pode ser posterior a uma saída já registrada.")

                values["data_entrada"] = data.data_entrada
            
            if data.localizacao is not None:
                local_values = data.localizaca.model_dump(exclude_unset=True)

                for field, value in local_values.items():
                    setattr(estoque, field, value)

            
            if values:
                await EntradaRepository.update(db, entrada, values)

            await db.flush()
            await db.commit()

            return await EntradaService.find_by_id(db, entrada.id)

        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()
            
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar a entrada.")
        except Exception:
            await db.rollback()
            raise