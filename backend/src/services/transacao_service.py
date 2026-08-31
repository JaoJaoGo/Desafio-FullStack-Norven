from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.produto_repository import ProdutoRepository
from repositories.transacao_repository import TransacaoRepository
from schemas.transacao_schema import TransacaoFilterSchema, TransacaoResponseSchema

class TransacaoService:
    @staticmethod
    async def list_by_product(db: AsyncSession, produto_id: int, filters: TransacaoFilterSchema):
        produto = await ProdutoRepository.find_by_id(db, produto_id)

        if produto is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado.")

        rows, total = await TransacaoRepository.list_by_product(db, produto_id, filters)

        items = [TransacaoResponseSchema(**row) for row in rows]

        return items, total