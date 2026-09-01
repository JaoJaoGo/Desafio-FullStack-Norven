from httpx import AsyncClient

from core.configs import settings

from tests.integration.api.payloads import build_fornecedor_payload

FORNECEDORES_URL = f"{settings.API_V1_STR}/fornecedores/"

async def test_criar_fornecedor(client: AsyncClient, auth_headers: dict, municipio_id: int):
    payload = build_fornecedor_payload(municipio_id, 1)

    response = await client.post(FORNECEDORES_URL, json=payload, headers=auth_headers)
    assert response.status_code == 201

    body = response.json()

    assert body["id"] is not None
    assert body["nome"] == payload["nome"]
    assert body["cnpj"] == payload["cnpj"]

    assert body["endereco_id"] is not None
    assert body["contato_id"] is not None

    assert body["endereco"]["logradouro"] == payload["endereco"]["logradouro"]
    assert body["contato"]["numero"] == payload["contato"]["numero"]

async def test_criar_fornecedor_exige_autenticacao(client: AsyncClient, municipio_id: int):
    payload = build_fornecedor_payload(municipio_id, 2)

    response = await client.post(FORNECEDORES_URL, json=payload)

    assert response.status_code == 401

async def test_nao_permite_cnpj_duplicado(client: AsyncClient, auth_headers: dict, municipio_id: int):
    primeiro = build_fornecedor_payload(municipio_id, 3)
    segundo = build_fornecedor_payload(municipio_id, 4)

    segundo["cnpj"] = primeiro["cnpj"]

    primeira_response = await client.post(FORNECEDORES_URL, json=primeiro, headers=auth_headers)
    assert primeira_response.status_code == 201

    segunda_response = await client.post(FORNECEDORES_URL, json=segundo, headers=auth_headers)
    assert segunda_response.status_code == 409

    assert segunda_response.json()["detail"] == "Já existe fornecedor com este CNPJ"

async def test_cnpj_deve_possuir_14_digitos(client: AsyncClient, auth_headers: dict, municipio_id: int):
    payload = build_fornecedor_payload(municipio_id, 5)
    payload["cnpj"] = "123"

    response = await client.post(FORNECEDORES_URL, json=payload, headers=auth_headers)

    assert response.status_code == 422

async def test_listar_fornecedores(client: AsyncClient, auth_headers: dict, municipio_id: int):
    for indice in [6, 7, 8]:
        response = await client.post(FORNECEDORES_URL, json=build_fornecedor_payload(municipio_id, indice), headers=auth_headers)

        assert response.status_code == 201

    response = await client.get(FORNECEDORES_URL, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert body["page"] == 1
    assert body["per_page"] == 20

    assert len(body["items"]) == 3

async def test_pesquisar_fornecedor_por_nome(client: AsyncClient, auth_headers: dict, municipio_id: int):
    for indice in [9, 10]:
        response = await client.post(FORNECEDORES_URL, json=build_fornecedor_payload(municipio_id, indice), headers=auth_headers)

        assert response.status_code == 201

    response = await client.get(FORNECEDORES_URL, params={"search": "Fornecedor Teste 10"}, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["nome"] == "Fornecedor Teste 10"


async def test_buscar_fornecedor_por_id(client: AsyncClient, auth_headers: dict, municipio_id: int):
    payload = build_fornecedor_payload(municipio_id, 11)

    create_response = await client.post(FORNECEDORES_URL, json=payload, headers=auth_headers)
    assert create_response.status_code == 201

    fornecedor_id = create_response.json()["id"]

    response = await client.get(f"{FORNECEDORES_URL}{fornecedor_id}", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["id"] == fornecedor_id
    assert body["nome"] == payload["nome"]
    assert body["cnpj"] == payload["cnpj"]


async def test_buscar_fornecedor_inexistente(client: AsyncClient, auth_headers: dict):
    response = await client.get( f"{FORNECEDORES_URL}999999", headers=auth_headers)
    assert response.status_code == 404

    assert response.json()["detail"] == "Fornecedor não encontrado."

async def test_editar_fornecedor(client: AsyncClient, auth_headers: dict, municipio_id: int):
    payload = build_fornecedor_payload(municipio_id, 12)

    create_response = await client.post(FORNECEDORES_URL, json=payload, headers=auth_headers)
    assert create_response.status_code == 201
    fornecedor_id = create_response.json()["id"]

    response = await client.patch(f"{FORNECEDORES_URL}{fornecedor_id}", json={"nome": ("Fornecedor Atualizado"), "endereco": {"logradouro": "Avenida do Fornecedor"}, "contato": {
                "numero": "977777777"}}, headers=auth_headers
    )
    assert response.status_code == 200

    body = response.json()

    assert body["nome"] == "Fornecedor Atualizado"
    assert body["endereco"]["logradouro"] == "Avenida do Fornecedor"
    assert body["contato"]["numero"] == "977777777"

async def test_reutiliza_endereco_e_contato_identicos(client: AsyncClient, auth_headers: dict, municipio_id: int):
    primeiro = build_fornecedor_payload(municipio_id, 13)

    segundo = build_fornecedor_payload(municipio_id, 14)
    segundo["endereco"] = primeiro["endereco"].copy()
    segundo["contato"] = primeiro["contato"].copy()

    primeira_response = await client.post(FORNECEDORES_URL, json=primeiro, headers=auth_headers)
    assert primeira_response.status_code == 201

    segunda_response = await client.post(FORNECEDORES_URL, json=segundo, headers=auth_headers)
    assert segunda_response.status_code == 201

    primeiro_body = primeira_response.json()
    segundo_body = segunda_response.json()

    assert primeiro_body["endereco_id"] == segundo_body["endereco_id"]
    assert primeiro_body["contato_id"] == segundo_body["contato_id"]
