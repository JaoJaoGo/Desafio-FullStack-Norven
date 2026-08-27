import asyncio
import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT_DIR / "src"))

from core.database import Session
from seeders.geography_seeder import seed_geography

async def run() -> None:
    async with Session() as session:
        try:
            async with session.begin():
                await seed_geography(session)

            print("Banco populado com sucesso!")
        except Exception:
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(run())