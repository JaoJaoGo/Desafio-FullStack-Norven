import asyncio
from importlib import import_module

from seeders.bootstrap import SRC_DIR  # noqa: F401

# Registra todos os models e relationships no SQLAlchemy.
import_module("models.__all_models")

from core.database import database
from seeders.admin_seeder import seed_admin
from seeders.geography_seeder import seed_geography


async def run() -> None:
    print("Começando a seedar dados iniciais...")

    async with database.session_factory() as session:
        try:
            async with session.begin():
                await seed_geography(session)

                print(
                    "Seeding usuário administrador..."
                )

                await seed_admin(session)

            print(
                "Dados iniciais populados com sucesso!"
            )

        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(run())
