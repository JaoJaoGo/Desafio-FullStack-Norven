from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker

from core.configs import settings

class Database:
    _instance = None

    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]

    def __new__(cls) -> "Database":
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._instance.engine = create_async_engine(settings.DB_URL)

            cls._instance.session_factory = async_sessionmaker(
                bind=cls._instance.engine,
                class_=AsyncSession,
                autoflush=False,
                expire_on_commit=False,
            )

        return cls._instance

database = Database()