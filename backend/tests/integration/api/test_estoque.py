from httpx import AsyncClient

from tests.integration.api.helpers_movimentacoes import ESTOQUES_URL, criar_cenario_movimentacao, criar_entrada, decimal_json

async def test_estoque_e_criado_automaticamente_pela_entrada(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=21)

    entrada = await criar_entrada(client, auth_headers, cenario, indice=21, quantidade="30.000")

    response = await client.get(f"{ESTOQUES_URL}{entrada['estoque_id']}", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["id"] == entrada["estoque_id"]
    assert body["entrada_id"] == entrada["id"]
    assert body["produto_id"] == cenario["produto"]["id"]
    assert body["lote_id"] == cenario["lote"]["id"]
    assert decimal_json(body["quantidade_atual"]) == decimal_json("30.000")

async def test_listar_estoques(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=22)

    await criar_entrada(client, auth_headers, cenario, indice=22, quantidade="15.000")

    response = await client.get(ESTOQUES_URL, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["page"] == 1
    assert body["per_page"] == 20
    assert len(body["items"]) == 1

async def test_filtrar_estoque_por_produto(client: AsyncClient, auth_headers: dict, municipio_id: int):
    primeiro = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=23)
    segundo = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=24)

    await criar_entrada(client, auth_headers, primeiro, indice=23)

    entrada_segundo = await criar_entrada(client, auth_headers, segundo, indice=24)

    response = await client.get(ESTOQUES_URL, params={"produto_id": segundo["produto"]["id"]}, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["id"] == entrada_segundo["estoque_id"]
    assert body["items"][0]["produto_id"] == segundo["produto"]["id"]

async def test_filtrar_estoque_por_lote(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=25)

    entrada = await criar_entrada(client, auth_headers, cenario, indice=25)

    response = await client.get(ESTOQUES_URL, params={"lote_id": cenario["lote"]["id"]}, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["id"] == entrada["estoque_id"]

async def test_editar_localizacao_do_estoque(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=26)

    entrada = await criar_entrada(client, auth_headers, cenario, indice=26)

    response = await client.patch(
        f"{ESTOQUES_URL}{entrada['estoque_id']}",
        json={"corredor": "CORREDOR-99", "prateleira": "PRATELEIRA-99", "secao": "SECAO-99"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    body = response.json()

    assert body["corredor"] == "CORREDOR-99"
    assert body["prateleira"] == "PRATELEIRA-99"
    assert body["secao"] == "SECAO-99"

async def test_buscar_estoque_inexistente(client: AsyncClient, auth_headers: dict):
    response = await client.get(f"{ESTOQUES_URL}999999", headers=auth_headers)

    assert response.status_code == 404

async def test_nao_permite_criar_estoque_diretamente(client: AsyncClient, auth_headers: dict):
    response = await client.post(ESTOQUES_URL, json={"quantidade_atual": "100.000", "corredor": "A", "prateleira": "B", "secao": "C", "entrada_id": 1}, headers=auth_headers)

    assert response.status_code == 405

async def test_estoques_exigem_autenticacao(client: AsyncClient):
    response = await client.get(ESTOQUES_URL)

    assert response.status_code == 401