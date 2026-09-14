import asyncio
from importlib import import_module

from seeders.bootstrap import SRC_DIR  # noqa: F401

# Registra todos os models e relationships no SQLAlchemy.
import_module("models.__all_models")

from core.database import database
from seeders.admin_seeder import seed_admin
from seeders.application_seeder import seed_application
from seeders.geography_seeder import seed_geography
from seeders.usuario_seeder import SEED_USER_PASSWORD

async def run() -> None:
    print("Começando o seeding completo...")

    async with database.session_factory() as session:
        try:
            async with session.begin():
                await seed_geography(session)

                print("Seeding usuário administrador...")

                await seed_admin(session)
                await seed_application(session)

            print("Banco populado com sucesso!")
            print(f"Senha dos usuários de teste: {SEED_USER_PASSWORD}")

        except Exception as e:
            print(f"Erro ao seedar banco completo: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(run())