from datetime import datetime
from httpx import AsyncClient

from tests.integration.api.helpers_movimentacoes import ENTRADAS_URL, ESTOQUES_URL, PRODUTOS_URL, SAIDAS_URL, criar_cenario_movimentacao, criar_entrada, decimal_json
from tests.integration.api.payloads import build_entrada_payload, build_saida_payload

async def test_criar_saida_de_venda_reduz_estoque_e_registra_auditoria(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=31)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=31, quantidade="10.000")

    response = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="3.000", tipo_saida="VENDA"),
        headers=auth_headers,
    )
    assert response.status_code == 201

    body = response.json()

    assert body["id"] is not None
    assert body["produto_id"] == cenario["produto"]["id"]
    assert body["estoque_id"] == entrada["estoque_id"]
    assert body["lote_id"] == cenario["lote"]["id"]

    assert decimal_json(body["quantidade"]) == decimal_json("3.000")

    assert body["tipo_saida"] == "VENDA"

    assert decimal_json(body["preco_venda_unitario"]) == decimal_json(cenario["produto"]["preco_venda_atual"])

    assert body["usuario_id"] is not None
    assert body["usuario_nome"]
    assert body["data_saida"] is not None

    estoque_response = await client.get(f"{ESTOQUES_URL}{entrada['estoque_id']}", headers=auth_headers)
    assert estoque_response.status_code == 200

    assert decimal_json(estoque_response.json()["quantidade_atual"]) == decimal_json("7.000")

async def test_criar_saida_exige_autenticacao(client: AsyncClient):
    response = await client.post(SAIDAS_URL, json=build_saida_payload(produto_id=1, estoque_id=1))

    assert response.status_code == 401

async def test_saida_exige_estoque_existente(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=32)

    response = await client.post(SAIDAS_URL, json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=999999), headers=auth_headers)

    assert response.status_code == 404

async def test_estoque_da_saida_deve_pertencer_ao_produto(client: AsyncClient, auth_headers: dict, municipio_id: int):
    primeiro = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=33)
    segundo = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=34)

    entrada_primeiro = await criar_entrada(client, auth_headers, primeiro, indice=33)

    response = await client.post(SAIDAS_URL, json=build_saida_payload(produto_id=segundo["produto"]["id"], estoque_id=entrada_primeiro["estoque_id"]), headers=auth_headers)
    assert response.status_code == 409

async def test_nao_permite_saida_maior_que_estoque(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=35)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=35, quantidade="10.000")

    response = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="11.000"),
        headers=auth_headers
    )
    assert response.status_code == 409

    estoque_response = await client.get(f"{ESTOQUES_URL}{entrada['estoque_id']}", headers=auth_headers)
    assert estoque_response.status_code == 200
    assert decimal_json(estoque_response.json()["quantidade_atual"]) == decimal_json("10.000")

async def test_saida_nao_venda_nao_permite_preco(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=36)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=36)

    response = await client.post(SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="1.000", tipo_saida="PERDA", preco_venda_unitario="12.50"),
        headers=auth_headers
    )
    assert response.status_code == 422

async def test_saida_por_perda_nao_possui_preco(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=37)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=37)

    response = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="2.000", tipo_saida="PERDA"),
        headers=auth_headers
    )
    assert response.status_code == 201

    body = response.json()

    assert body["tipo_saida"] == "PERDA"
    assert body["preco_venda_unitario"] is None

async def test_saida_nao_pode_ocorrer_antes_da_entrada(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=38)

    entrada_response = await client.post(
        ENTRADAS_URL,
        json=build_entrada_payload(
            produto_id=cenario["produto"]["id"],
            fornecedor_id=cenario["fornecedor"]["id"],
            lote_id=cenario["lote"]["id"],
            indice=38,
            quantidade="10.000",
            data_entrada=datetime(2026, 9, 1, 12, 0, 0)
        ),
        headers=auth_headers
    )
    assert entrada_response.status_code == 201

    entrada = entrada_response.json()

    response = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(
            produto_id=cenario["produto"]["id"],
            estoque_id=entrada["estoque_id"],
            quantidade="1.000",
            tipo_saida="PERDA",
            data_saida=datetime(2026, 8, 31, 12, 0, 0)
        ),
        headers=auth_headers
    )
    assert response.status_code == 422

async def test_listar_e_filtrar_saidas(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=39)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=39, quantidade="20.000")

    venda = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="1.000", tipo_saida="VENDA"),
        headers=auth_headers
    )

    perda = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="2.000", tipo_saida="PERDA"),
        headers=auth_headers
    )

    assert venda.status_code == 201
    assert perda.status_code == 201

    response = await client.get(
        SAIDAS_URL,
        params={"produto_id": cenario["produto"]["id"], "tipo_saida": "PERDA", "quantidade_min": "1.500", "quantidade_max": "2.500"},
        headers=auth_headers
    )
    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["tipo_saida"] == "PERDA"
    assert decimal_json(body["items"][0]["quantidade"]) == decimal_json("2.000")

async def test_buscar_saida_por_id(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=40)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=40)

    create_response = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="2.000", tipo_saida="PERDA"),
        headers=auth_headers
    )
    assert create_response.status_code == 201

    saida_id = create_response.json()["id"]

    response = await client.get(f"{SAIDAS_URL}{saida_id}", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["id"] == saida_id
    assert body["produto_id"] == cenario["produto"]["id"]
    assert body["estoque_id"] == entrada["estoque_id"]

async def test_buscar_saida_inexistente(client: AsyncClient, auth_headers: dict):
    response = await client.get(f"{SAIDAS_URL}999999", headers=auth_headers)

    assert response.status_code == 404

async def test_editar_quantidade_da_saida_recalcula_estoque(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=41)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=41, quantidade="10.000")

    create_response = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="3.000", tipo_saida="PERDA"),
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    saida_id = create_response.json()["id"]

    aumentar = await client.patch(f"{SAIDAS_URL}{saida_id}", json={"quantidade": "5.000"}, headers=auth_headers)
    assert aumentar.status_code == 200

    estoque_apos_aumento = await client.get(f"{ESTOQUES_URL}{entrada['estoque_id']}", headers=auth_headers)
    assert estoque_apos_aumento.status_code == 200
    assert decimal_json(estoque_apos_aumento.json()["quantidade_atual"]) == decimal_json("5.000")

    diminuir = await client.patch(f"{SAIDAS_URL}{saida_id}", json={"quantidade": "2.000"}, headers=auth_headers)
    assert diminuir.status_code == 200

    estoque_apos_reducao = await client.get(f"{ESTOQUES_URL}{entrada['estoque_id']}", headers=auth_headers)
    assert estoque_apos_reducao.status_code == 200
    assert decimal_json(estoque_apos_reducao.json()["quantidade_atual"]) == decimal_json("8.000")

async def test_nao_permite_aumentar_saida_acima_do_saldo_disponivel(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=42)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=42, quantidade="10.000")

    create_response = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="8.000", tipo_saida="PERDA"),
        headers=auth_headers
    )
    assert create_response.status_code == 201

    saida_id = create_response.json()["id"]

    response = await client.patch(f"{SAIDAS_URL}{saida_id}", json={"quantidade": "11.000"}, headers=auth_headers)
    assert response.status_code == 409

    estoque_response = await client.get(f"{ESTOQUES_URL}{entrada['estoque_id']}", headers=auth_headers)
    assert estoque_response.status_code == 200
    assert decimal_json(estoque_response.json()["quantidade_atual"]) == decimal_json("2.000")

async def test_alterar_venda_para_perda_remove_preco(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=43)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=43)

    create_response = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="1.000", tipo_saida="VENDA"),
        headers=auth_headers
    )
    assert create_response.status_code == 201

    saida_id = create_response.json()["id"]

    response = await client.patch(f"{SAIDAS_URL}{saida_id}", json={"tipo_saida": "PERDA"}, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["tipo_saida"] == "PERDA"
    assert body["preco_venda_unitario"] is None

async def test_entrada_nao_pode_ser_reduzida_abaixo_do_total_ja_retirado(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=44)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=44, quantidade="10.000")

    saida_response = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="4.000", tipo_saida="PERDA"),
        headers=auth_headers
    )
    assert saida_response.status_code == 201

    response = await client.patch(f"{ENTRADAS_URL}{entrada['id']}", json={"quantidade": "3.000"}, headers=auth_headers)
    assert response.status_code == 400

    estoque_response = await client.get(f"{ESTOQUES_URL}{entrada['estoque_id']}", headers=auth_headers)
    assert estoque_response.status_code == 200
    assert decimal_json(estoque_response.json()["quantidade_atual"]) == decimal_json("6.000")

async def test_historico_do_produto_reune_entrada_e_saida(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=45)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=45, quantidade="10.000")

    saida_response = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="2.000", tipo_saida="VENDA"),
        headers=auth_headers
    )
    assert saida_response.status_code == 201

    historico_url = (f"{PRODUTOS_URL}{cenario['produto']['id']}/transacoes")

    response = await client.get(historico_url, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()
    assert body["total"] == 2

    movimentos = {item["movimento"] for item in body["items"]}
    assert movimentos == {"ENTRADA", "SAIDA"}

    apenas_saidas = await client.get(historico_url, params={"movimento": "SAIDA"}, headers=auth_headers)
    assert apenas_saidas.status_code == 200

    body_saidas = apenas_saidas.json()

    assert body_saidas["total"] == 1
    assert body_saidas["items"][0]["movimento"] == "SAIDA"

async def test_nao_permite_excluir_saida(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=46)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=46)

    create_response = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(produto_id=cenario["produto"]["id"], estoque_id=entrada["estoque_id"], quantidade="1.000", tipo_saida="PERDA"),
        headers=auth_headers
    )
    assert create_response.status_code == 201

    saida_id = create_response.json()["id"]

    response = await client.delete(f"{SAIDAS_URL}{saida_id}", headers=auth_headers)
    assert response.status_code == 405

async def test_listagem_de_saidas_exige_autenticacao(client: AsyncClient):
    response = await client.get(SAIDAS_URL)

    assert response.status_code == 401