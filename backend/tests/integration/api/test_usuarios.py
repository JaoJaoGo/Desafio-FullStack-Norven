from httpx import AsyncClient

from core.configs import settings

from tests.integration.api.payloads import build_usuario_payload

USUARIOS_URL = f"{settings.API_V1_STR}/usuarios/"

LOGIN_URL = f"{settings.API_V1_STR}/auth/login"

async def test_criar_usuario(client: AsyncClient, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 1)

    response = await client.post(USUARIOS_URL, json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["id"] is not None
    assert body["nome"] == payload["nome"]
    assert body["email"] == payload["email"]

    assert body["nivel_acesso"] == "operador"

    assert body["endereco_id"] is not None
    assert body["contato_id"] is not None
    
    assert "password" not in body
    assert "senha" not in body

async def test_usuario_criado_consegue_fazer_login(client: AsyncClient, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 2)
    
    response = await client.post(USUARIOS_URL, json=payload)
    assert response.status_code == 201
    
    login_response = await client.post(LOGIN_URL, data={"username": payload["email"], "password": payload["password"]})

    assert login_response.status_code == 200
    body = login_response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"

async def test_nao_permite_usuario_com_email_duplicado(client: AsyncClient, municipio_id: int):
    primeiro = build_usuario_payload(municipio_id, 3)
    segundo = build_usuario_payload(municipio_id, 4)

    segundo["email"] = primeiro["email"]

    primeiro_response = await client.post(USUARIOS_URL, json=primeiro)
    assert primeiro_response.status_code == 201

    segunda_response = await client.post(USUARIOS_URL, json=segundo)
    assert segunda_response.status_code == 409

    assert segunda_response.json()["detail"] == "Já existe um usuário com este e-mail."

async def test_nao_permite_senha_menor_que_o_minimo(client: AsyncClient, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 5)
    payload["password"] = "1234567"

    response = await client.post(USUARIOS_URL, json=payload)

    assert response.status_code == 422

async def test_listar_usuarios(client: AsyncClient, auth_headers: dict, municipio_id: int):
    for indice in [6, 7]:
        payload = build_usuario_payload(municipio_id, indice)

        response = await client.post(USUARIOS_URL, json=payload)
        assert response.status_code == 201

    response = await client.get(USUARIOS_URL, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    # Existe também o admin criado pelo seeder.
    assert body["total"] == 3
    assert body["page"] == 1
    assert body["per_page"] == 20

    nomes = {item["nome"] for item in body["items"]}
    assert "Usuário Teste 6" in nomes
    assert "Usuário Teste 7" in nomes

async def test_pesquisar_usuario_por_email(client: AsyncClient, auth_headers: dict, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 8)

    create_response = await client.post(USUARIOS_URL, json=payload)
    assert create_response.status_code == 201

    response = await client.get(USUARIOS_URL, headers=auth_headers, params={"search": payload["email"]})
    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["email"] == payload["email"]

async def test_buscar_usuario_por_id(client: AsyncClient, auth_headers: dict, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 9)

    create_response = await client.post(USUARIOS_URL, json=payload)
    assert create_response.status_code == 201

    usuario_id = create_response.json()["id"]
    
    response = await client.get(f"{USUARIOS_URL}{usuario_id}", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["id"] == usuario_id
    assert body["nome"] == payload["nome"]
    assert body["email"] == payload["email"]
    assert body["endereco"]["logradouro"] == payload["endereco"]["logradouro"]
    assert body["contato"]["numero"] == payload["contato"]["numero"]

async def test_buscar_usuario_inexistente(client: AsyncClient, auth_headers: dict):
    response = await client.get(f"{USUARIOS_URL}999999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Usuário não encontrado."

async def test_editar_usuario(client: AsyncClient, auth_headers: dict, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 10)

    create_response = await client.post(USUARIOS_URL, json=payload)
    assert create_response.status_code == 201

    usuario_id = create_response.json()["id"]

    response = await client.patch(f"{USUARIOS_URL}{usuario_id}", json={"nome": "Usuário Atualizado", "nivel_acesso": "administrador"}, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert (body["nome"] == "Usuário Atualizado")
    assert (body["nivel_acesso"] == "administrador")

async def test_listagem_de_usuarios_exige_autenticacao(client: AsyncClient):
    response = await client.get(USUARIOS_URL)

    assert response.status_code == 401

async def test_consulta_de_usuario_exige_autenticacao(client: AsyncClient):
    response = await client.get(f"{USUARIOS_URL}1")

    assert response.status_code == 401