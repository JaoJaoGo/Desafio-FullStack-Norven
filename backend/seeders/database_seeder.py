import asyncio
import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT_DIR / "src")
)

# Registra todos os models e relationships no SQLAlchemy
import models.__all_models  # noqa: F401

from core.database import Session

from seeders.admin_seeder import seed_admin
from seeders.geography_seeder import seed_geography

async def run() -> None:
    print("Começando a seedar...")

    async with Session() as session:
        try:
            async with session.begin():
                await seed_geography(session)

                print("Seeding usuário administrador...")
                await seed_admin(session)

            print("Banco populado com sucesso!")

        except Exception:
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(run())