from httpx import AsyncClient

from core.configs import settings

LOGIN_URL = f"{settings.API_V1_STR}/auth/login"

async def test_login_com_credenciais_validas(client: AsyncClient, auth_credentials: dict):
    response = await client.post(LOGIN_URL, data={"username": auth_credentials["email"], "password": auth_credentials["password"]})

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 0
    assert body["token_type"] == "bearer"

async def test_login_com_senha_incorreta(client: AsyncClient, auth_credentials: dict):
    response = await client.post(LOGIN_URL, data={"username": auth_credentials["email"], "password": "senha-incorreta"})
    
    assert response.status_code == 401

    body = response.json()

    assert body["detail"] == "E-mail ou senha inválidos."

async def test_login_com_email_inexistente(client: AsyncClient):
    response = await client.post(LOGIN_URL, data={"username": "email-inexistente@exemplo.com", "password": "senha-qualquer"})

    assert response.status_code == 401

    body = response.json()

    assert body["detail"] == "E-mail ou senha inválidos."

async def test_login_sem_senha(client: AsyncClient, auth_credentials: dict):
    response = await client.post(LOGIN_URL, data={"username": auth_credentials["email"]})

    assert response.status_code == 422

async def test_login_sem_email(client: AsyncClient, auth_credentials: dict):
    response = await client.post(LOGIN_URL, data={"password": auth_credentials["password"]})

    assert response.status_code == 422