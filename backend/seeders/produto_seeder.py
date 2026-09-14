from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.engine.result import Result
from sqlalchemy.sql.selectable import Select
from decimal import Decimal
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from seeders.bootstrap import SRC_DIR  # noqa: F401
from models.categoria_model import CategoriaModel
from models.informacao_nutricional_model import InformacaoNutricionalModel
from models.produto_model import ProdutoModel
from models.unidade_medida_model import UnidadeMedidaModel
from models.usuario_model import UsuarioModel

PRODUTOS = [
    ("SEED-PROD-001", "Arroz Tipo 1 5kg", "Alimentos Básicos", "kg", "NUT-001", Decimal("29.90"), False),
    ("SEED-PROD-002", "Feijão Carioca 1kg", "Alimentos Básicos", "kg", "NUT-002", Decimal("8.99"), False),
    ("SEED-PROD-003", "Macarrão Espaguete 500g", "Mercearia", "g", "NUT-003", Decimal("5.49"), False),
    ("SEED-PROD-004", "Açúcar Cristal 5kg", "Alimentos Básicos", "kg", "NUT-004", Decimal("19.90"), False),
    ("SEED-PROD-005", "Café Torrado 500g", "Mercearia", "g", "NUT-005", Decimal("18.50"), False),
    ("SEED-PROD-006", "Leite Integral 1L", "Laticínios", "L", "NUT-006", Decimal("5.99"), True),
    ("SEED-PROD-007", "Iogurte Natural 170g", "Laticínios", "g", "NUT-007", Decimal("4.49"), True),
    ("SEED-PROD-008", "Queijo Mussarela 500g", "Laticínios", "g", "NUT-008", Decimal("24.90"), True),
    ("SEED-PROD-009", "Refrigerante Cola 2L", "Bebidas", "L", "NUT-009", Decimal("10.99"), False),
    ("SEED-PROD-010", "Suco de Laranja 1L", "Bebidas", "L", "NUT-010", Decimal("12.50"), False),
    ("SEED-PROD-011", "Água Mineral 1,5L", "Bebidas", "L", None, Decimal("3.49"), False),
    ("SEED-PROD-012", "Patinho Bovino 1kg", "Carnes", "kg", "NUT-011", Decimal("42.90"), True),
    ("SEED-PROD-013", "Peito de Frango 1kg", "Carnes", "kg", "NUT-012", Decimal("18.90"), True),
    ("SEED-PROD-014", "Linguiça Toscana 1kg", "Carnes", "kg", "NUT-013", Decimal("22.90"), True),
    ("SEED-PROD-015", "Banana Prata 1kg", "Hortifruti", "kg", "NUT-014", Decimal("7.49"), True),
    ("SEED-PROD-016", "Maçã Gala 1kg", "Hortifruti", "kg", "NUT-015", Decimal("12.90"), True),
    ("SEED-PROD-017", "Tomate Italiano 1kg", "Hortifruti", "kg", None, Decimal("9.49"), True),
    ("SEED-PROD-018", "Pão Francês 1kg", "Padaria", "kg", "NUT-016", Decimal("16.90"), True),
    ("SEED-PROD-019", "Pão de Forma 500g", "Padaria", "g", "NUT-017", Decimal("9.90"), True),
    ("SEED-PROD-020", "Bolo de Chocolate 500g", "Padaria", "g", None, Decimal("21.90"), True),
    ("SEED-PROD-021", "Pizza Congelada 460g", "Congelados", "g", "NUT-018", Decimal("18.90"), True),
    ("SEED-PROD-022", "Lasanha Congelada 600g", "Congelados", "g", None, Decimal("21.50"), True),
    ("SEED-PROD-023", "Sabonete Neutro 90g", "Higiene", "un", None, Decimal("3.99"), False),
    ("SEED-PROD-024", "Shampoo 350mL", "Higiene", "mL", None, Decimal("16.90"), False),
    ("SEED-PROD-025", "Detergente 500mL", "Limpeza", "mL", None, Decimal("2.89"), False),
    ("SEED-PROD-026", "Água Sanitária 2L", "Limpeza", "L", None, Decimal("8.49"), False),
    ("SEED-PROD-027", "Papel Higiênico 12 Rolos", "Higiene", "pct", None, Decimal("19.90"), False),
    ("SEED-PROD-028", "Biscoito Cream Cracker 350g", "Mercearia", "g", "NUT-019", Decimal("6.99"), False),
    ("SEED-PROD-029", "Óleo de Soja 900mL", "Alimentos Básicos", "mL", "NUT-020", Decimal("7.49"), False),
    ("SEED-PROD-030", "Farinha de Trigo 1kg", "Alimentos Básicos", "kg", None, Decimal("6.49"), False),
]

async def seed_produtos(
    session: AsyncSession,
    categorias: dict[str, CategoriaModel],
    unidades: dict[str, UnidadeMedidaModel],
    informacoes: dict[str, InformacaoNutricionalModel],
    usuarios: dict[str, UsuarioModel],
) -> dict[str, ProdutoModel]:
    print("Seeding produtos...")

    responsaveis: list[UsuarioModel] = list(usuarios.values())

    if not responsaveis:
        raise RuntimeError("Nenhum usuário de teste foi encontrado.")

    result: dict[str, ProdutoModel] = {}

    for index, item in enumerate(PRODUTOS):
        (
            codigo,
            nome,
            categoria_nome,
            unidade_sigla,
            nutricao_key,
            preco,
            perecivel,
        ) = item

        query: Select[tuple[ProdutoModel]] = select(ProdutoModel).where(
            or_(
                ProdutoModel.cod_idt == codigo,
                ProdutoModel.nome == nome,
            )
        )

        query_result: Result[tuple[ProdutoModel]] = await session.execute(query)
        produto: ProdutoModel | None = query_result.scalar_one_or_none()

        responsavel: UsuarioModel = responsaveis[index % len(responsaveis)]

        informacao: InformacaoNutricionalModel | None = informacoes[nutricao_key] if nutricao_key is not None else None

        values: dict[str, Decimal | InstrumentedAttribute[int] | bool | str | None] = {
            "cod_idt": codigo,
            "nome": nome,
            "descricao": f"Produto de teste gerado pelo seeder: {nome}.",
            "preco_venda_atual": preco,
            "eh_perecivel": perecivel,
            "usuario_id": responsavel.id,
            "categoria_id": categorias[categoria_nome].id,
            "unidade_medida_id": unidades[unidade_sigla].id,
            "informacao_nutricional_id": informacao.id if informacao is not None else None,
        }

        if produto is None:
            produto = ProdutoModel(**values)
            session.add(produto)
        else:
            for field, value in values.items():
                setattr(produto, field, value)

        await session.flush()
        result[codigo] = produto

    return result