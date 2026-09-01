from datetime import date, timedelta
from httpx import AsyncClient

from tests.integration.api.helpers_movimentacoes import ENTRADAS_URL, criar_cenario_movimentacao, criar_entrada, decimal_json
from tests.integration.api.payloads import build_entrada_payload

async def test_criar_entrada_cria_estoque_e_registra_auditoria(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=1)

    payload = build_entrada_payload(
        produto_id=cenario["produto"]["id"],
        fornecedor_id=cenario["fornecedor"]["id"],
        lote_id=cenario["lote"]["id"],
        indice=1,
        quantidade="10.000",
        preco_custo_unitario="5.50",
        tipo_entrada="compra",
    )

    response = await client.post(ENTRADAS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 201

    body = response.json()

    assert body["id"] is not None
    assert body["produto_id"] == cenario["produto"]["id"]
    assert body["fornecedor_id"] == cenario["fornecedor"]["id"]
    assert body["lote_id"] == cenario["lote"]["id"]

    assert decimal_json(body["quantidade"]) == decimal_json("10.000")
    assert decimal_json(body["preco_custo_unitario"]) == decimal_json("5.50")

    assert body["tipo_entrada"] == "COMPRA"

    assert body["usuario_id"] is not None
    assert body["usuario_nome"]
    assert body["data_entrada"] is not None

    assert body["estoque_id"] is not None
    assert decimal_json(body["quantidade_atual"]) == decimal_json("10.000")

    assert body["corredor"] == "C1"
    assert body["prateleira"] == "P1"
    assert body["secao"] == "S1"

async def test_criar_entrada_exige_autenticacao(client: AsyncClient):
    response = await client.post(ENTRADAS_URL, json=build_entrada_payload(produto_id=1, fornecedor_id=1, lote_id=1))

    assert response.status_code == 401

async def test_entrada_exige_produto_existente(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=2)

    payload = build_entrada_payload(produto_id=999999, fornecedor_id=cenario["fornecedor"]["id"], lote_id=cenario["lote"]["id"], indice=2)

    response = await client.post(ENTRADAS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 404

async def test_entrada_exige_fornecedor_existente(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=3)

    payload = build_entrada_payload(produto_id=cenario["produto"]["id"], fornecedor_id=999999, lote_id=cenario["lote"]["id"], indice=3)

    response = await client.post(ENTRADAS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 404

async def test_lote_da_entrada_deve_pertencer_ao_produto(client: AsyncClient, auth_headers: dict, municipio_id: int):
    primeiro = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=4)
    segundo = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=5)

    payload = build_entrada_payload(produto_id=primeiro["produto"]["id"], fornecedor_id=primeiro["fornecedor"]["id"], lote_id=segundo["lote"]["id"], indice=4)

    response = await client.post(ENTRADAS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 409

async def test_entrada_exige_exatamente_um_tipo_de_lote(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=6)

    sem_lote = build_entrada_payload(produto_id=cenario["produto"]["id"], fornecedor_id=cenario["fornecedor"]["id"], lote_id=None, indice=6)

    response_sem_lote = await client.post(ENTRADAS_URL, json=sem_lote, headers=auth_headers)
    assert response_sem_lote.status_code == 422

    com_dois_lotes = build_entrada_payload(
        produto_id=cenario["produto"]["id"],
        fornecedor_id=cenario["fornecedor"]["id"],
        lote_id=cenario["lote"]["id"],
        indice=6,
        novo_lote={"numero": "NOVO-LOTE-006", "data_validade": (date.today() + timedelta(days=90)).isoformat()},
    )

    response_dois_lotes = await client.post(ENTRADAS_URL, json=com_dois_lotes, headers=auth_headers)
    assert response_dois_lotes.status_code == 422

async def test_entrada_pode_criar_novo_lote(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=7)

    payload = build_entrada_payload(
        produto_id=cenario["produto"]["id"],
        fornecedor_id=cenario["fornecedor"]["id"],
        lote_id=None,
        indice=7,
        novo_lote={"numero": "LOTE-NOVO-007", "data_validade": (date.today() + timedelta(days=120)).isoformat()},
    )

    response = await client.post(ENTRADAS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 201

    body = response.json()

    assert body["produto_id"] == cenario["produto"]["id"]
    assert body["lote_numero"] == "LOTE-NOVO-007"
    assert body["lote_id"] != cenario["lote"]["id"]

async def test_listar_e_filtrar_entradas(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=8)

    primeira = await client.post(
        ENTRADAS_URL,
        json=build_entrada_payload(
            produto_id=cenario["produto"]["id"], fornecedor_id=cenario["fornecedor"]["id"], lote_id=cenario["lote"]["id"], indice=8, quantidade="10.000", tipo_entrada="COMPRA"
        ),
        headers=auth_headers,
    )

    segunda = await client.post(
        ENTRADAS_URL,
        json=build_entrada_payload(
            produto_id=cenario["produto"]["id"], fornecedor_id=cenario["fornecedor"]["id"], lote_id=cenario["lote"]["id"], indice=9, quantidade="25.000", tipo_entrada="AJUSTE"
        ),
        headers=auth_headers,
    )

    assert primeira.status_code == 201
    assert segunda.status_code == 201

    response = await client.get(
        ENTRADAS_URL,
        params={"produto_id": cenario["produto"]["id"], "fornecedor_id": cenario["fornecedor"]["id"], "tipo_entrada": "AJUSTE", "quantidade_min": "20", "quantidade_max": "30"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["tipo_entrada"] == "AJUSTE"
    assert decimal_json(body["items"][0]["quantidade"]) == decimal_json("25.000")

async def test_buscar_entrada_por_id(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=10)

    entrada = await criar_entrada(client, auth_headers, cenario, indice=10)

    response = await client.get(f"{ENTRADAS_URL}{entrada['id']}", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["id"] == entrada["id"]
    assert body["produto_id"] == cenario["produto"]["id"]
    assert body["lote_id"] == cenario["lote"]["id"]

async def test_buscar_entrada_inexistente(client: AsyncClient, auth_headers: dict):
    response = await client.get(f"{ENTRADAS_URL}999999", headers=auth_headers)

    assert response.status_code == 404

async def test_editar_quantidade_da_entrada_atualiza_estoque(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=11)

    entrada = await criar_entrada(client, auth_headers, cenario, indice=11, quantidade="10.000")

    response = await client.patch(f"{ENTRADAS_URL}{entrada['id']}", json={"quantidade": "15.000"}, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert decimal_json(body["quantidade"]) == decimal_json("15.000")
    assert decimal_json(body["quantidade_atual"]) == decimal_json("15.000")

async def test_editar_localizacao_pela_entrada(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=12)

    entrada = await criar_entrada(client, auth_headers, cenario, indice=12)

    response = await client.patch(
        f"{ENTRADAS_URL}{entrada['id']}",
        json={"localizacao": {"corredor": "CORREDOR-NOVO", "prateleira": "PRATELEIRA-NOVA", "secao": "SECAO-NOVA"}},
        headers=auth_headers
    )
    assert response.status_code == 200

    body = response.json()

    assert body["corredor"] == "CORREDOR-NOVO"
    assert body["prateleira"] == "PRATELEIRA-NOVA"
    assert body["secao"] == "SECAO-NOVA"

async def test_nao_permite_excluir_entrada(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=13)

    entrada = await criar_entrada(client, auth_headers, cenario, indice=13)

    response = await client.delete(f"{ENTRADAS_URL}{entrada['id']}", headers=auth_headers)
    assert response.status_code == 405

async def test_listagem_de_entradas_exige_autenticacao(client: AsyncClient):
    response = await client.get(ENTRADAS_URL)

    assert response.status_code == 401