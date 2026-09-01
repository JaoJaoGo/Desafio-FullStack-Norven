from httpx import AsyncClient

from core.configs import settings

CATEGORIAS_URL = f"{settings.API_V1_STR}/categorias/"

async def test_criar_categoria(client: AsyncClient, auth_headers: dict):
    response = await client.post(CATEGORIAS_URL, json={"nome": "Bebidas"}, headers=auth_headers)

    assert response.status_code == 201

    body = response.json()

    assert body["id"] is not None
    assert body["nome"] == "Bebidas"

async def test_nao_permite_categoria_duplicada(client: AsyncClient, auth_headers: dict):
    primeira_response = await client.post(CATEGORIAS_URL, json={"nome": "Laticínios"}, headers=auth_headers)

    assert primeira_response.status_code == 201

    segunda_response = await client.post(CATEGORIAS_URL, json={"nome": "Laticínios"}, headers=auth_headers)

    assert segunda_response.status_code == 409

    body = segunda_response.json()

    assert body["detail"] == "Já existe uma categoria com este nome."

async def test_listar_categorias(client: AsyncClient, auth_headers: dict):
    nomes = [
        "Bebidas",
        "Carnes",
        "Laticínios",
    ]

    for nome in nomes:
        response = await client.post(CATEGORIAS_URL, json={"nome": nome}, headers=auth_headers)

        assert response.status_code == 201

    response = await client.get(CATEGORIAS_URL, headers=auth_headers)

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert body["page"] == 1
    assert body["per_page"] == 20

    assert len(body["items"]) == 3

    nomes_retornados = [item["nome"] for item in body["items"]]

    assert nomes_retornados == [
        "Bebidas",
        "Carnes",
        "Laticínios",
    ]

async def test_listar_categorias_com_paginacao(client: AsyncClient, auth_headers: dict):
    nomes = [
        "Bebidas",
        "Carnes",
        "Congelados",
        "Hortifruti",
        "Laticínios",
    ]

    for nome in nomes:
        response = await client.post(CATEGORIAS_URL, json={"nome": nome}, headers=auth_headers)

        assert response.status_code == 201

    response = await client.get(CATEGORIAS_URL, params={"page": 2, "per_page": 2}, headers=auth_headers)

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 5
    assert body["page"] == 2
    assert body["per_page"] == 2

    assert len(body["items"]) == 2

    assert [item["nome"] for item in body["items"]] == ["Congelados", "Hortifruti"]

async def test_pesquisar_categoria_por_nome(client: AsyncClient, auth_headers: dict):
    for nome in [
        "Bebidas",
        "Carnes",
        "Laticínios",
    ]:

        response = await client.post(CATEGORIAS_URL, json={"nome": nome}, headers=auth_headers)

        assert response.status_code == 201

    response = await client.get(CATEGORIAS_URL, params={"search": "lati"}, headers=auth_headers)

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1

    assert len(body["items"]) == 1

    assert body["items"][0]["nome"] == "Laticínios"

async def test_buscar_categoria_por_id(client: AsyncClient, auth_headers: dict):
    create_response = await client.post(CATEGORIAS_URL, json={"nome": "Padaria"}, headers=auth_headers)

    assert create_response.status_code == 201

    categoria_id = create_response.json()["id"]

    response = await client.get(f"{CATEGORIAS_URL}{categoria_id}", headers=auth_headers)

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == categoria_id
    assert body["nome"] == "Padaria"

async def test_buscar_categoria_inexistente(client: AsyncClient, auth_headers: dict):
    response = await client.get(f"{CATEGORIAS_URL}999999", headers=auth_headers)

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "Categoria não encontrada."

async def test_editar_categoria(client: AsyncClient, auth_headers: dict):
    create_response = await client.post(CATEGORIAS_URL, json={"nome": "Bebida"}, headers=auth_headers)

    assert create_response.status_code == 201

    categoria_id = create_response.json()["id"]

    response = await client.patch(f"{CATEGORIAS_URL}{categoria_id}", json={"nome": "Bebidas"}, headers=auth_headers)

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == categoria_id
    assert body["nome"] == "Bebidas"

async def test_nao_permite_editar_categoria_para_nome_existente(client: AsyncClient, auth_headers: dict):
    primeira = await client.post(CATEGORIAS_URL, json={"nome": "Bebidas"}, headers=auth_headers)

    segunda = await client.post(CATEGORIAS_URL, json={"nome": "Carnes"}, headers=auth_headers)

    assert primeira.status_code == 201
    assert segunda.status_code == 201

    categoria_carnes_id = segunda.json()["id"]

    response = await client.patch(f"{CATEGORIAS_URL}{categoria_carnes_id}", json={"nome": "Bebidas"}, headers=auth_headers)

    assert response.status_code == 409

async def test_categoria_exige_autenticacao(client: AsyncClient):
    response = await client.get(CATEGORIAS_URL)

    assert response.status_code == 401