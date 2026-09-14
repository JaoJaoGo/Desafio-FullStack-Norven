from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from seeders.bootstrap import SRC_DIR  # noqa: F401

from models.categoria_model import CategoriaModel

CATEGORIAS: list[str] = [
    "Alimentos Básicos",
    "Bebidas",
    "Laticínios",
    "Carnes",
    "Hortifruti",
    "Padaria",
    "Congelados",
    "Higiene",
    "Limpeza",
    "Mercearia",
]

async def seed_categorias(session: AsyncSession) -> dict[str, CategoriaModel]:
    print("Seeding categorias...")

    result: dict[str, CategoriaModel] = {}

    for nome in CATEGORIAS:
        query = select(CategoriaModel).where(CategoriaModel.nome == nome)

        query_result = await session.execute(query)
        categoria = query_result.scalar_one_or_none()

        if categoria is None:
            categoria = CategoriaModel(nome=nome)
            session.add(categoria)
            await session.flush()
        
        result[nome] = categoria

    return result