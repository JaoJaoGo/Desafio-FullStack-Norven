from httpx import AsyncClient
import pytest
from pydantic import ValidationError

from core.configs import settings
from tests.integration.api.helpers_movimentacoes import (
    ENTRADAS_URL,
    PRODUTOS_URL,
    SAIDAS_URL,
    criar_cenario_movimentacao,
    criar_entrada,
    decimal_json,
)
from tests.integration.api.payloads import build_saida_payload

TRANSACOES_URL = f"{settings.API_V1_STR}/transacoes/"


async def criar_cenario_com_transacoes(client: AsyncClient, auth_headers: dict, municipio_id: int, indice: int = 1) -> tuple[dict, dict, dict]:
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=indice)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=indice, quantidade="10.000")

    saida_response = await client.post(
        SAIDAS_URL,
        json=build_saida_payload(
            produto_id=cenario["produto"]["id"],
            estoque_id=entrada["estoque_id"],
            quantidade="3.000",
            tipo_saida="PERDA",
        ),
        headers=auth_headers,
    )
    assert saida_response.status_code == 201

    return cenario, entrada, saida_response.json()


async def test_listar_transacoes_reune_entradas_e_saidas(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario, entrada, saida = await criar_cenario_com_transacoes(client, auth_headers, municipio_id, indice=1)

    response = await client.get(TRANSACOES_URL, params={"produto_id": cenario["produto"]["id"], "per_page": 20}, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert {item["movimento"] for item in body["items"]} == {"ENTRADA", "SAIDA"}
    assert {item["id"] for item in body["items"]} == {entrada["id"], saida["id"]}


async def test_listar_transacoes_aplica_filtros_de_movimento_tipo_e_quantidade(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario, _, _ = await criar_cenario_com_transacoes(client, auth_headers, municipio_id, indice=2)
    produto_id = cenario["produto"]["id"]

    entrada_response = await client.get(
        TRANSACOES_URL,
        params={"produto_id": produto_id, "movimento": "ENTRADA", "tipo": "compra", "quantidade": "10.000", "per_page": 20},
        headers=auth_headers,
    )
    saida_response = await client.get(
        TRANSACOES_URL,
        params={"produto_id": produto_id, "movimento": "SAIDA", "tipo": "perda", "quantidade_min": "2.000", "quantidade_max": "4.000", "per_page": 20},
        headers=auth_headers,
    )

    assert entrada_response.status_code == 200
    assert saida_response.status_code == 200
    entrada_body = entrada_response.json()
    saida_body = saida_response.json()
    assert entrada_body["total"] == 1
    assert entrada_body["items"][0]["tipo"] == "COMPRA"
    assert decimal_json(entrada_body["items"][0]["quantidade"]) == decimal_json("10.000")
    assert saida_body["total"] == 1
    assert saida_body["items"][0]["tipo"] == "PERDA"
    assert decimal_json(saida_body["items"][0]["quantidade"]) == decimal_json("3.000")


async def test_listar_transacoes_pesquisa_por_produto(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario, _, _ = await criar_cenario_com_transacoes(client, auth_headers, municipio_id, indice=3)

    response = await client.get(TRANSACOES_URL, params={"search": "Produto Teste 3", "per_page": 20}, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert all(item["produto_id"] == cenario["produto"]["id"] for item in body["items"])


async def test_listar_transacoes_respeita_paginacao(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario, _, _ = await criar_cenario_com_transacoes(client, auth_headers, municipio_id, indice=4)

    primeira = await client.get(TRANSACOES_URL, params={"produto_id": cenario["produto"]["id"], "page": 1, "per_page": 1}, headers=auth_headers)
    segunda = await client.get(TRANSACOES_URL, params={"produto_id": cenario["produto"]["id"], "page": 2, "per_page": 1}, headers=auth_headers)

    assert primeira.status_code == 200
    assert segunda.status_code == 200
    assert primeira.json()["total"] == 2
    assert segunda.json()["total"] == 2
    assert len(primeira.json()["items"]) == 1
    assert len(segunda.json()["items"]) == 1
    assert primeira.json()["items"][0]["movimento"] != segunda.json()["items"][0]["movimento"]


async def test_listar_transacoes_por_produto_e_filtra_produto_inexistente(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario, _, _ = await criar_cenario_com_transacoes(client, auth_headers, municipio_id, indice=5)

    response = await client.get(f"{PRODUTOS_URL}{cenario['produto']['id']}/transacoes", params={"movimento": "ENTRADA"}, headers=auth_headers)
    inexistente = await client.get(f"{PRODUTOS_URL}999999/transacoes", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["produto_id"] == cenario["produto"]["id"]
    assert inexistente.status_code == 404


async def test_filtros_de_transacoes_com_intervalo_invalido_retorna_422(client: AsyncClient, auth_headers: dict):
    with pytest.raises(ValidationError, match="quantidade_min"):
        await client.get(TRANSACOES_URL, params={"quantidade_min": "5", "quantidade_max": "2"}, headers=auth_headers)

    with pytest.raises(ValidationError, match="data_inicio"):
        await client.get(TRANSACOES_URL, params={"data_inicio": "2026-02-01T00:00:00", "data_fim": "2026-01-01T00:00:00"}, headers=auth_headers)


async def test_transacoes_exigem_autenticacao(client: AsyncClient):
    response = await client.get(TRANSACOES_URL)
    produto_response = await client.get(f"{PRODUTOS_URL}1/transacoes")

    assert response.status_code == 401
    assert produto_response.status_code == 401


async def test_criar_entrada_pela_rota_do_produto(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=6)
    payload = {
        "fornecedor_id": cenario["fornecedor"]["id"],
        "lote_id": cenario["lote"]["id"],
        "quantidade": "7.000",
        "preco_custo_unitario": "4.25",
        "tipo_entrada": "COMPRA",
        "localizacao": {"corredor": "C6", "prateleira": "P6", "secao": "S6"},
    }

    response = await client.post(
        f"{PRODUTOS_URL}{cenario['produto']['id']}/transacoes/entrada",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["produto_id"] == cenario["produto"]["id"]
    assert decimal_json(body["quantidade"]) == decimal_json("7.000")


async def test_criar_saida_pela_rota_do_produto(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario, entrada, _ = await criar_cenario_com_transacoes(client, auth_headers, municipio_id, indice=7)
    payload = {
        "estoque_id": entrada["estoque_id"],
        "quantidade": "2.000",
        "tipo_saida": "AVARIA",
    }

    response = await client.post(
        f"{PRODUTOS_URL}{cenario['produto']['id']}/transacoes/saida",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["produto_id"] == cenario["produto"]["id"]
    assert body["tipo_saida"] == "AVARIA"


async def test_rotas_aninhadas_rejeitam_produto_inexistente(client: AsyncClient, auth_headers: dict, municipio_id: int):
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=8)
    entrada_payload = {
        "fornecedor_id": cenario["fornecedor"]["id"],
        "lote_id": cenario["lote"]["id"],
        "quantidade": "1.000",
        "preco_custo_unitario": "4.25",
        "tipo_entrada": "COMPRA",
        "localizacao": {"corredor": "C8", "prateleira": "P8", "secao": "S8"},
    }
    saida_payload = {"estoque_id": 999999, "quantidade": "1.000", "tipo_saida": "PERDA"}

    entrada_response = await client.post(f"{PRODUTOS_URL}999999/transacoes/entrada", json=entrada_payload, headers=auth_headers)
    saida_response = await client.post(f"{PRODUTOS_URL}999999/transacoes/saida", json=saida_payload, headers=auth_headers)

    assert entrada_response.status_code == 404
    assert saida_response.status_code == 404


async def test_saida_aninhada_rejeita_estoque_de_outro_produto(client: AsyncClient, auth_headers: dict, municipio_id: int):
    primeiro, _, _ = await criar_cenario_com_transacoes(client, auth_headers, municipio_id, indice=9)
    segundo, segunda_entrada = await criar_entrada_para_produto_diferente(client, auth_headers, municipio_id)

    response = await client.post(
        f"{PRODUTOS_URL}{primeiro['produto']['id']}/transacoes/saida",
        json={"estoque_id": segunda_entrada["estoque_id"], "quantidade": "1.000", "tipo_saida": "PERDA"},
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert segundo["produto"]["id"] != primeiro["produto"]["id"]


async def criar_entrada_para_produto_diferente(client: AsyncClient, auth_headers: dict, municipio_id: int) -> tuple[dict, dict]:
    cenario = await criar_cenario_movimentacao(client, auth_headers, municipio_id, indice=10)
    entrada = await criar_entrada(client, auth_headers, cenario, indice=10, quantidade="5.000")
    return cenario, entrada
