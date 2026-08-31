from sqlalchemy.ext.asyncio import AsyncSession

from models.usuario_model import UsuarioModel

from schemas.produto_schema import ProdutoCreateSchema, ProdutoFilterSchema, ProdutoUpdateSchema

from services.produto_service import ProdutoService

class ProdutoController:
    @staticmethod
    async def create(data: ProdutoCreateSchema, db: AsyncSession, current_user: UsuarioModel):
        return await ProdutoService.create(db, data, current_user)

    @staticmethod
    async def list(db: AsyncSession, filters: ProdutoFilterSchema):
        return await ProdutoService.list(db, filters)

    @staticmethod
    async def find_by_id(produto_id: int, db: AsyncSession):
        return await ProdutoService.find_by_id(db, produto_id)


    @staticmethod
    async def update(produto_id: int, data: ProdutoUpdateSchema, db: AsyncSession):
        return await ProdutoService.update(db, produto_id, data)
