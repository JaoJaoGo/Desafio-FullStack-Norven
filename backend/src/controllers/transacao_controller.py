from sqlalchemy.ext.asyncio import AsyncSession

from schemas.transacao_schema import TransacaoFilterSchema
from services.transacao_service import TransacaoService

class TransacaoController:
    @staticmethod
    async def list_by_product(db: AsyncSession, produto_id: int, filters: TransacaoFilterSchema):
        return await TransacaoService.list_by_product(db, produto_id, filters)