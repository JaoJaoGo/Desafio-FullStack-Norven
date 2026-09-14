from models.estoque_model import EstoqueModel
from models.lote_model import LoteModel
from models.produto_model import ProdutoModel
from models.informacao_nutricional_model import InformacaoNutricionalModel
from models.fornecedor_model import FornecedorModel
from models.usuario_model import UsuarioModel
from models.unidade_medida_model import UnidadeMedidaModel
from models.categoria_model import CategoriaModel
import asyncio
from importlib import import_module

from sqlalchemy.ext.asyncio import AsyncSession

from seeders.bootstrap import SRC_DIR  # noqa: F401

# Registra todos os models e relationships no SQLAlchemy.
import_module("models.__all_models")

from core.database import database
from seeders.categoria_seeder import seed_categorias
from seeders.entrada_seeder import seed_entradas
from seeders.fornecedor_seeder import seed_fornecedores
from seeders.informacao_nutricional_seeder import seed_informacoes_nutricionais
from seeders.lote_seeder import seed_lotes
from seeders.produto_seeder import seed_produtos
from seeders.saida_seeder import seed_saidas
from seeders.unidade_medida_seeder import seed_unidades_medidas
from seeders.usuario_seeder import SEED_USER_PASSWORD, seed_usuarios

async def seed_application(session: AsyncSession) -> None:
    categorias: dict[str, CategoriaModel] = await seed_categorias(session)
    unidades: dict[str, UnidadeMedidaModel] = await seed_unidades_medidas(session)
    usuarios: dict[str, UsuarioModel] = await seed_usuarios(session)
    fornecedores: dict[str, FornecedorModel] = await seed_fornecedores(session)
    informacoes: dict[str, InformacaoNutricionalModel] = await seed_informacoes_nutricionais(session, unidades)
    produtos: dict[str, ProdutoModel] = await seed_produtos(session, categorias, unidades, informacoes, usuarios)
    lotes: dict[str, LoteModel] = await seed_lotes(session, produtos)
    estoques: dict[str, EstoqueModel] = await seed_entradas(session, lotes, fornecedores, usuarios)

    await seed_saidas(session, estoques, usuarios)

async def run() -> None:
    print("Começando a seedar dados de aplicação...")

    async with database.session_factory() as session:
        try:
            async with session.begin():
                await seed_application(session)

            print("Dados de aplicação populados com sucesso!")
            print(f"Senha dos usuários de teste: {SEED_USER_PASSWORD}")

        except Exception as e:
            print(f"Erro ao seedar dados de aplicação: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(run())