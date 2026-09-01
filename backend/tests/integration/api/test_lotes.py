from datetime import date, timedelta
from httpx import AsyncClient

from core.configs import settings
from tests.integration.api.payloads import build_lote_payload, build_produto_payload

PRODUTOS_URL = f"{settings.API_V1_STR}/produtos/"
LOTES_URL = f"{settings.API_V1_STR}/lotes/"
CATEGORIAS_URL = f"{settings.API_V1_STR}/categorias/"
UNIDADES_URL = f"{settings.API_V1_STR}/unidades-medidas/"

async def criar_catalogo_base(client: AsyncClient, auth_headers: dict) -> tuple[int, int]:
    categoria_response = await client.post(CATEGORIAS_URL, json={"nome": "Alimentos"}, headers=auth_headers)

    assert categoria_response.status_code == 201

    unidade_response = await client.post(UNIDADES_URL, json={"nome": "Unidade", "sigla": "un"}, headers=auth_headers)

    assert unidade_response.status_code == 201
    return (categoria_response.json()["id"], unidade_response.json()["id"])

async def criar_produto(client: AsyncClient, auth_headers: dict, categoria_id: int, unidade_id: int, indice: int, eh_perecivel: bool) -> dict:
    response = await client.post(PRODUTOS_URL, json=build_produto_payload(categoria_id=categoria_id, unidade_medida_id=unidade_id, indice=indice, eh_perecivel=eh_perecivel),
        headers=auth_headers
    )

    assert response.status_code == 201

    return response.json()

async def test_criar_lote_para_produto_perecivel(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)
    produto = await criar_produto(client, auth_headers, categoria_id, unidade_id, 1, True)
    validade = date.today() + timedelta(days=60)

    payload = build_lote_payload(produto_id=produto["id"], indice=1, data_validade=validade)

    response = await client.post(LOTES_URL, json=payload, headers=auth_headers)
    assert response.status_code == 201

    body = response.json()

    assert body["id"] is not None
    assert body["numero"] == payload["numero"]
    assert body["produto_id"] == produto["id"]
    assert body["data_validade"] == validade.isoformat()

async def test_produto_perecivel_exige_validade_no_lote(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)
    produto = await criar_produto(client, auth_headers, categoria_id, unidade_id, 2, True)

    payload = build_lote_payload(produto_id=produto["id"], indice=2, data_validade=None)

    response = await client.post(LOTES_URL, json=payload, headers=auth_headers)
    assert response.status_code == 422

async def test_produto_nao_perecivel_permite_lote_sem_validade(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)
    produto = await criar_produto(client, auth_headers, categoria_id, unidade_id, 3, False)

    payload = build_lote_payload(produto_id=produto["id"], indice=3, data_validade=None)

    response = await client.post(LOTES_URL, json=payload, headers=auth_headers)
    assert response.status_code == 201

    body = response.json()

    assert body["data_validade"] is None

async def test_produto_nao_perecivel_tambem_permite_validade(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)
    produto = await criar_produto(client, auth_headers, categoria_id, unidade_id, 4, False)
    validade = date.today() + timedelta(days=365)

    response = await client.post(LOTES_URL, json=build_lote_payload(produto_id=produto["id"], indice=4, data_validade=validade), headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["data_validade"] == validade.isoformat()


async def test_lote_exige_produto_existente(client: AsyncClient, auth_headers: dict):
    validade = date.today() + timedelta(days=30)

    response = await client.post(LOTES_URL, json=build_lote_payload(produto_id=999999, indice=5, data_validade=validade), headers=auth_headers)
    assert response.status_code == 404

async def test_nao_permite_numero_de_lote_duplicado_no_mesmo_produto(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)
    produto = await criar_produto(client, auth_headers, categoria_id, unidade_id, 6, True)
    validade = date.today() + timedelta(days=60)

    payload = build_lote_payload(produto_id=produto["id"], indice=6, data_validade=validade)

    primeira_response = await client.post(LOTES_URL, json=payload, headers=auth_headers)
    assert primeira_response.status_code == 201

    segunda_response = await client.post(LOTES_URL, json=payload, headers=auth_headers)
    assert segunda_response.status_code == 409

async def test_permite_mesmo_numero_de_lote_em_produtos_diferentes(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)
    produto_1 = await criar_produto(client, auth_headers, categoria_id, unidade_id, 7, True)
    produto_2 = await criar_produto(client, auth_headers, categoria_id, unidade_id, 8, True)

    validade = date.today() + timedelta(days=60)

    primeiro = build_lote_payload(produto_id=produto_1["id"], indice=7, data_validade=validade)
    segundo = build_lote_payload(produto_id=produto_2["id"], indice=8, data_validade=validade)

    segundo["numero"] = primeiro["numero"]

    primeira_response = await client.post(LOTES_URL, json=primeiro, headers=auth_headers)
    segunda_response = await client.post(LOTES_URL, json=segundo, headers=auth_headers)

    assert primeira_response.status_code == 201
    assert segunda_response.status_code == 201

async def test_listar_lotes(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)
    produto = await criar_produto(client, auth_headers, categoria_id, unidade_id, 9, True)

    for indice, dias in [(9, 30), (10, 60), (11, 90)]:
        response = await client.post(LOTES_URL, json=build_lote_payload(produto_id=produto["id"], indice=indice, data_validade=(date.today() + timedelta(days=dias))),
            headers=auth_headers
        )

        assert response.status_code == 201

    response = await client.get(LOTES_URL, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert body["page"] == 1
    assert body["per_page"] == 20

    assert len(body["items"]) == 3

async def test_buscar_lote_por_id(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)
    produto = await criar_produto(client, auth_headers, categoria_id, unidade_id, 12, True)
    validade = date.today() + timedelta(days=90)

    create_response = await client.post(LOTES_URL, json=build_lote_payload(produto_id=produto["id"], indice=12, data_validade=validade), headers=auth_headers)
    assert create_response.status_code == 201

    lote_id = create_response.json()["id"]

    response = await client.get(f"{LOTES_URL}{lote_id}", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["id"] == lote_id
    assert body["produto_id"] == produto["id"]
    assert body["data_validade"] == validade.isoformat()

async def test_buscar_lote_inexistente(client: AsyncClient, auth_headers: dict):
    response = await client.get(f"{LOTES_URL}999999", headers=auth_headers)

    assert response.status_code == 404

async def test_editar_numero_do_lote(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)
    produto = await criar_produto(client, auth_headers, categoria_id, unidade_id, 13, True)

    validade = date.today() + timedelta(days=60)

    create_response = await client.post(LOTES_URL, json=build_lote_payload(produto_id=produto["id"], indice=13, data_validade=validade), headers=auth_headers)
    assert create_response.status_code == 201

    lote_id = create_response.json()["id"]

    response = await client.patch(f"{LOTES_URL}{lote_id}", json={"numero": "LOTE-ATUALIZADO"}, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["numero"] == "LOTE-ATUALIZADO"
    assert body["produto_id"] == produto["id"]
    assert body["data_validade"] == validade.isoformat()

async def test_nao_permite_converter_para_perecivel_se_existir_lote_sem_validade(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)
    produto = await criar_produto(client, auth_headers, categoria_id, unidade_id, 14, False)

    lote_response = await client.post(LOTES_URL, json=build_lote_payload(produto_id=produto["id"], indice=14, data_validade=None), headers=auth_headers)
    assert lote_response.status_code == 201

    response = await client.patch(f"{PRODUTOS_URL}{produto['id']}", json={"eh_perecivel": True}, headers=auth_headers)
    assert response.status_code == 409

async def test_permite_converter_para_perecivel_quando_todos_lotes_possuem_validade(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)
    produto = await criar_produto(client, auth_headers, categoria_id, unidade_id, 15, False)

    validade = date.today() + timedelta(days=180)

    lote_response = await client.post(LOTES_URL, json=build_lote_payload(produto_id=produto["id"], indice=15, data_validade=validade), headers=auth_headers)
    assert lote_response.status_code == 201

    response = await client.patch(f"{PRODUTOS_URL}{produto['id']}", json={"eh_perecivel": True}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["eh_perecivel"] is True

async def test_criar_lote_exige_autenticacao(client: AsyncClient):
    response = await client.post(LOTES_URL, json={})

    assert response.status_code == 401

async def test_listar_lotes_exige_autenticacao(client: AsyncClient):
    response = await client.get(LOTES_URL)

    assert response.status_code == 401