from sqlalchemy.sql.selectable import Select
from sqlalchemy.engine.result import Result
import asyncio
from datetime import date
from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from seeders.bootstrap import SRC_DIR  # noqa: F401
from core.configs import settings
from core.database import database
from models.categoria_model import CategoriaModel
from models.entrada_model import EntradaModel
from models.estoque_model import EstoqueModel
from models.fornecedor_model import FornecedorModel
from models.informacao_nutricional_model import InformacaoNutricionalModel
from models.lote_model import LoteModel
from models.produto_model import ProdutoModel
from models.saida_model import SaidaModel
from models.unidade_medida_model import UnidadeMedidaModel
from models.usuario_model import UsuarioModel

async def _count(session: AsyncSession, model) -> int:
    result: Result[tuple[int]] = await session.execute(
        select(func.count()).select_from(model)
    )

    return result.scalar_one()

async def _stock_total(session: AsyncSession, product_code: str) -> Decimal:
    query: Select[tuple[Decimal]] = (
        select(func.coalesce(func.sum(EstoqueModel.quantidade_atual), Decimal("0")))
        .select_from(ProdutoModel)
        .join(LoteModel, LoteModel.produto_id == ProdutoModel.id)
        .join(EntradaModel, EntradaModel.lote_id == LoteModel.id)
        .join(EstoqueModel, EstoqueModel.entrada_id == EntradaModel.id)
        .where(ProdutoModel.cod_idt == product_code)
    )

    result: Result[tuple[Decimal]] = await session.execute(query)

    return Decimal(result.scalar_one())

async def run() -> None:
    async with database.session_factory() as session:
        counts: dict[str, int] = {
            "categorias": await _count(session, CategoriaModel),
            "unidades_medidas": await _count(session, UnidadeMedidaModel),
            "funcionarios": await _count(session, UsuarioModel),
            "fornecedores": await _count(session, FornecedorModel),
            "informacoes_nutricionais": await _count(session, InformacaoNutricionalModel),
            "produtos": await _count(session, ProdutoModel),
            "lotes": await _count(session, LoteModel),
            "entradas": await _count(session, EntradaModel),
            "estoques": await _count(session, EstoqueModel),
            "saidas": await _count(session, SaidaModel),
        }

        print("Contagens:")
        for name, count in counts.items():
            print(f"  {name}: {count}")

        assert counts["categorias"] >= 10
        assert counts["unidades_medidas"] >= 10
        assert counts["funcionarios"] >= 10
        assert counts["fornecedores"] >= 10
        assert counts["produtos"] >= 30
        assert counts["lotes"] >= 40
        assert counts["entradas"] >= 40
        assert counts["estoques"] >= 40
        assert counts["saidas"] >= 30

        product_1_stock: Decimal = await _stock_total(session, "SEED-PROD-001")
        product_3_stock: Decimal = await _stock_total(session, "SEED-PROD-003")

        low_limit: Decimal = Decimal(str(settings.ESTOQUE_BAIXO_LIMITE))

        assert product_1_stock > 0
        assert low_limit <= 0 or product_1_stock <= low_limit

        assert product_3_stock == 0

        expired_query: Select[tuple[int]] = (
            select(func.count(LoteModel.id))
            .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
            .join(EntradaModel, EntradaModel.lote_id == LoteModel.id)
            .join(EstoqueModel, EstoqueModel.entrada_id == EntradaModel.id)
            .where(
                ProdutoModel.cod_idt == "SEED-PROD-006",
                LoteModel.data_validade < date.today(),
                EstoqueModel.quantidade_atual > 0,
            )
        )

        result: Result[tuple[int]] = await session.execute(expired_query)

        assert result.scalar_one() > 0

        print("Verificação concluída com sucesso.")

if __name__ == "__main__":
    asyncio.run(run())