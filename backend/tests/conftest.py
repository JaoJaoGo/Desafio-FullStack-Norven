import os
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.engine import make_url

import models.__all_models
from core.configs import settings
from core.deps import get_session
from desafio_fullstack_norven.main import app
from models.usuario_model import UsuarioModel
from models.cidade_model import CidadeModel
from seeders.admin_seeder import seed_admin
from seeders.geography_seeder import seed_geography

# =======================================================
# CONFIGURAÇÃO DO BANCO DE DADOS DE TESTES
# =======================================================

TEST_DB_URL = os.getenv("TEST_DB_URL")

if not TEST_DB_URL:
    raise RuntimeError("A variável TEST_DB_URL não foi definida. Execute os testes utilizando 'docker-compose.test.yml'.")

test_database_name = make_url(TEST_DB_URL).database

if test_database_name is None or "test" not in test_database_name.lower():
    raise RuntimeError(f"Por segurança, o banco utilizado pelos testes precisa possuir 'test' no nome. Banco recebido: {test_database_name}")

# =======================================================
# ENGINE DE TESTE
#
# NullPool evita reutilização de conexões entre loops
# asyncio diferentes durante os testes.
# =======================================================

test_engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    poolclass=NullPool
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# =======================================================
# PREPARAÇÃO DO BANCO
#
# Executa UMA VEZ antes de todos os testes
# =======================================================

@pytest_asyncio.fixture(
    scope="session",
    loop_scope="session",
    autouse=True
)
async def prepare_test_database():
    """
    Prepara um PostgreSQL exclusivo para os testes.

    Fluxo:

    1. Limpa o schema public.
    2. Cria todas as tabelas a partir dos models.
    3. Popula país, estado e cidade.
    4. Cria o administrador inicial.
    5. Executa a suíte.
    6. Limpa o banco ao final.
    """

    metadata = settings.DBBaseModel.metadata

    # ---------------------------------------------------
    # RECRIA O SCHEMA
    # ---------------------------------------------------

    async with test_engine.begin() as connection:
        await connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))

        await connection.run_sync(metadata.create_all)

    # ---------------------------------------------------
    # SEED BASE
    # ---------------------------------------------------

    async with TestSessionLocal() as session:
        async with session.begin():
            await seed_geography(session)
            await seed_admin(session)
    
    yield

    # ---------------------------------------------------
    # LIMPEZA FINAL
    # ---------------------------------------------------

    async with test_engine.begin() as connection:
        await connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))
    
    await test_engine.dispose()

# =======================================================
# SESSÃO ISOLADA POR TESTE
# =======================================================

@pytest_asyncio.fixture
async def db_session(prepare_test_database) -> AsyncGenerator[AsyncSession, None]:
    """
    Cada teste recebe uma transação externa.

    Mesmo que um Service execute:
    
        await db.commit()
    
    as alterações continuam protegidas pela transação externa desta fixture.
    Ao terminar o teste:

        rollback()

    e o banco volta ao estado anterior.
    """
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        SessionForTest = async_sessionmaker(bind=connection, class_=AsyncSession, expire_on_commit=False, join_transaction_mode="create_savepoint")

        async with SessionForTest() as session:
            yield session

        await transaction.rollback()

# =======================================================
# OVERRIDE DO get_session
# =======================================================

@pytest_asyncio.fixture
async def override_database(db_session: AsyncSession):
    """
    Faz o FastAPI utilizar o banco de testes em vez
    da Session configurada no core/database.py.
    """

    async def override_get_session():
        yield db_session
    
    app.dependency_overrides[get_session] = override_get_session

    yield

    app.dependency_overrides.pop(get_session, None)

# =======================================================
# CLIENTE HTTP
# =======================================================

@pytest_asyncio.fixture
async def client(override_database) -> AsyncGenerator[AsyncClient, None]:
    """
    Cliente HTTP que chama o FastAPI diretamente.

    Não precisa acessar localhost:8000.
    """

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client

# =======================================================
# CIDADE PARA TESTES
# =======================================================

@pytest_asyncio.fixture
async def municipio_id(db_session: AsyncSession) -> int:
    result = await db_session.execute(select(CidadeModel.id).order_by(CidadeModel.id.asc()).limit(1))

    return result.scalar_one()

# =======================================================
# ADMINISTRADOR DE TESTE
# =======================================================

@pytest_asyncio.fixture
async def auth_credentials(db_session: AsyncSession):
    """
    Localiza o administrador criado pelo seed_admin.

    A senha utilizada pelo seeder vem das settings.
    """
    result = await db_session.execute(
        select(UsuarioModel).order_by(UsuarioModel.id.asc()).limit(1)
    )

    usuario = result.scalars().one()

    password = settings.PRIMARY_ADMIN_PASSWORD

    # Compatível caso no futuro a senha vire SecretStr.
    if hasattr(password, "get_secret_value"):
        password = password.get_secret_value()

    return {"email": usuario.email, "password": password}

# =======================================================
# TOKEN JWT
# =======================================================

@pytest_asyncio.fixture
async def access_token(client: AsyncClient, auth_credentials: dict) -> str:
    """
    Faz login pela API real e devolve o JWT.
    """

    response = await client.post((f"{settings.API_V1_STR}/auth/login"), data={"username": auth_credentials["email"], "password": auth_credentials["password"]})

    assert response.status_code == 200, f"Não foi possível autenticar o administrador usado pelos testes. Resposta: {response.text}"

    body = response.json()

    return body["access_token"]

# =======================================================
# HEADERS AUTENTICADOS
# =======================================================

@pytest.fixture
def auth_headers(access_token: str) -> dict[str, str]:
    """
    Header reutilizável pelos endpoints protegidos.
    """
    return {"Authorization": f"Bearer {access_token}"}