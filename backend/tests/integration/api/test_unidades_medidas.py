from httpx import AsyncClient

from core.configs import settings

UNIDADES_URL = f"{settings.API_V1_STR}/unidades-medidas/"

async def test_criar_unidade_medida(client: AsyncClient, auth_headers: dict):
    response = await client.post(UNIDADES_URL, headers=auth_headers, json={"nome": "Quilograma", "sigla": "kg"})

    assert response.status_code == 201

    body = response.json()

    assert body["id"] is not None
    assert body["nome"] == "Quilograma"
    assert body["sigla"] == "kg"

async def test_nao_permite_unidade_com_nome_duplicado(client: AsyncClient, auth_headers: dict):
    primeira = await client.post(UNIDADES_URL, headers=auth_headers, json={"nome": "Quilograma", "sigla": "kg"})

    assert primeira.status_code == 201
    
    segunda = await client.post(UNIDADES_URL, headers=auth_headers, json={"nome": "Quilograma", "sigla": "quilo"})

    assert segunda.status_code == 409

    body = segunda.json()

    assert body["detail"] == "Já existe uma unidade de medida com este nome."

async def test_nao_permite_unidade_com_sigla_duplicada(client: AsyncClient, auth_headers: dict):
    primeira = await client.post(UNIDADES_URL, headers=auth_headers, json={"nome": "Quilograma", "sigla": "kg"})

    assert primeira.status_code == 201

    segunda = await client.post(UNIDADES_URL, headers=auth_headers, json={"nome": "Quilo", "sigla": "kg"})

    assert segunda.status_code == 409

    body = segunda.json()

    assert body["detail"] == 'Já existe uma unidade de medida com esta sigla.'

async def test_listar_unidades_medidas(client: AsyncClient, auth_headers: dict):
    unidades = [
        {
            "nome": "Grama",
            "sigla": "g"
        },
        {
            "nome": "Litro",
            "sigla": "L"
        },
        {
            "nome": "Quilograma",
            "sigla": "kg"
        }
    ]

    for unidade in unidades:
        response = await client.post(UNIDADES_URL, headers=auth_headers, json=unidade)
        assert response.status_code == 201
    
    response = await client.get(UNIDADES_URL, headers=auth_headers)

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert body["page"] == 1
    assert body["per_page"] == 20

    assert len(body["items"]) == 3

    nomes = [
        item["nome"] for item in body["items"]
    ]

    assert nomes == [
        "Grama",
        "Litro",
        "Quilograma",
    ]

async def test_listar_unidades_com_paginacao(client: AsyncClient, auth_headers: dict):
    unidades = [
        {
            "nome": "Grama",
            "sigla": "g"
        },
        {
            "nome": "Litro",
            "sigla": "L"
        },
        {
            "nome": "Mililitro",
            "sigla": "mL"
        },
        {
            "nome": "Quilograma",
            "sigla": "kg"
        },
        {
            "nome": "Unidade",
            "sigla": "un"
        },
    ]

    for unidade in unidades:
        response = await client.post(UNIDADES_URL, headers=auth_headers, json=unidade)

        assert response.status_code == 201

    response = await client.get(UNIDADES_URL, headers=auth_headers, params={"page": 2, "per_page": 2})

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 5
    assert body["page"] == 2
    assert body["per_page"] == 2

    assert len(body["items"]) == 2

    nomes = [item["nome"] for item in body["items"]]

    assert nomes == [
        "Mililitro",
        "Quilograma",
    ]

async def test_pesquisar_unidade_por_nome(client: AsyncClient, auth_headers: dict):
    unidades = [
        {
            "nome": "Grama",
            "sigla": "g"
        },
        {
            "nome": "Litro",
            "sigla": "L"
        },
        {
            "nome": "Quilograma",
            "sigla": "kg"
        },
    ]

    for unidade in unidades:
        response = await client.post(UNIDADES_URL, headers=auth_headers, json=unidade)

        assert response.status_code == 201

    response = await client.get(UNIDADES_URL, headers=auth_headers, params={"search": "quilo"})

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["nome"] == "Quilograma"

async def test_pesquisar_unidade_por_sigla(client: AsyncClient, auth_headers: dict):
    unidades = [
        {
            "nome": "Grama",
            "sigla": "g",
        },
        {
            "nome": "Litro",
            "sigla": "L",
        },
        {
            "nome": "Quilograma",
            "sigla": "kg",
        },
    ]

    for unidade in unidades:
        response = await client.post(UNIDADES_URL, headers=auth_headers, json=unidade)

        assert response.status_code == 201
    
    response = await client.get(UNIDADES_URL, headers=auth_headers, params={"search": "kg"})

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["sigla"] == "kg"

async def test_buscar_unidade_por_id(client: AsyncClient, auth_headers: dict):
    create_response = await client.post(UNIDADES_URL, headers=auth_headers, json={"nome": "Litro", "sigla": "L"})

    assert create_response.status_code == 201

    unidade_id = create_response.json()["id"]

    response = await client.get(f"{UNIDADES_URL}{unidade_id}", headers=auth_headers)

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == unidade_id
    assert body["nome"] == "Litro"
    assert body["sigla"] == "L"

async def test_buscar_unidade_inexistente(client: AsyncClient, auth_headers: dict):
    response = await client.get(f"{UNIDADES_URL}999999", headers=auth_headers)

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "Unidade de medida não encontrada."

async def test_editar_unidade_medida(client: AsyncClient, auth_headers: dict):
    create_response = await client.post(UNIDADES_URL, headers=auth_headers, json={"nome": "Quilo", "sigla": "q"})

    assert create_response.status_code == 201

    unidade_id = create_response.json()["id"]

    response = await client.patch(f"{UNIDADES_URL}{unidade_id}", headers=auth_headers, json={"nome": "Quilograma", "sigla": "kg"})

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == unidade_id
    assert body["nome"] == "Quilograma"
    assert body["sigla"] == "kg"

async def test_nao_permite_editar_para_nome_existente(client: AsyncClient, auth_headers: dict):
    primeira = await client.post(UNIDADES_URL, headers=auth_headers, json={"nome": "Grama", "sigla": "g"})
    segunda = await client.post(UNIDADES_URL, headers=auth_headers, json={"nome": "Quilograma", "sigla": "kg"})

    assert primeira.status_code == 201
    assert segunda.status_code == 201

    unidade_id = segunda.json()["id"]

    response = await client.patch(f"{UNIDADES_URL}{unidade_id}", headers=auth_headers, json={"nome": "Grama"})

    assert response.status_code == 409

async def test_nao_permite_editar_para_sigla_existente(client: AsyncClient, auth_headers: dict):
    primeira = await client.post(UNIDADES_URL, headers=auth_headers, json={"nome": "Grama", "sigla": "g"})
    segunda = await client.post(UNIDADES_URL, headers=auth_headers, json={"nome": "Quilograma", "sigla": "kg"})

    assert primeira.status_code == 201
    assert segunda.status_code == 201

    unidade_id = segunda.json()["id"]

    response = await client.patch(f"{UNIDADES_URL}{unidade_id}", headers=auth_headers, json={"sigla": "g"})

    assert response.status_code == 409

async def test_unidades_medidas_exige_autenticacao(client: AsyncClient):
    response = await client.get(UNIDADES_URL)

    assert response.status_code == 401