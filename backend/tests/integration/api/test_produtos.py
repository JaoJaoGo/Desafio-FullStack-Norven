from decimal import Decimal
from httpx import AsyncClient

from core.configs import settings
from tests.integration.api.payloads import build_produto_payload

PRODUTOS_URL = f"{settings.API_V1_STR}/produtos/"
CATEGORIAS_URL = f"{settings.API_V1_STR}/categorias/"
UNIDADES_URL = f"{settings.API_V1_STR}/unidades-medidas/"

async def criar_catalogo_base(client: AsyncClient, auth_headers: dict) -> tuple[int, int]:
    categoria_response = await client.post(CATEGORIAS_URL, json={"nome": "Alimentos"}, headers=auth_headers)
    assert categoria_response.status_code == 201

    unidade_response = await client.post(UNIDADES_URL, json={"nome": "Unidade", "sigla": "un"}, headers=auth_headers)
    assert unidade_response.status_code == 201

    categoria_id = categoria_response.json()["id"]
    unidade_id = unidade_response.json()["id"]

    return categoria_id, unidade_id

async def test_criar_produto(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)

    payload = build_produto_payload(categoria_id=categoria_id, unidade_medida_id=unidade_id, indice=1)
    
    response = await client.post(PRODUTOS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 201

    body = response.json()

    assert body["id"] is not None
    assert body["cod_idt"] == payload["cod_idt"]
    assert body["nome"] == payload["nome"]
    assert body["descricao"] == payload["descricao"]
    assert Decimal(str(body["preco_venda_atual"])) == Decimal("12.50")
    assert body["eh_perecivel"] is False
    assert body["categoria_id"] == categoria_id
    assert body["unidade_medida_id"] == unidade_id
    assert body["usuario_id"] is not None

async def test_criar_produto_perecivel_sem_lote(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)

    payload = build_produto_payload(categoria_id=categoria_id, unidade_medida_id=unidade_id, indice=2, eh_perecivel=True)

    response = await client.post(PRODUTOS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 201

    body = response.json()

    assert body["eh_perecivel"] is True
    assert body.get('validade') is None

async def test_criar_produto_exige_autenticacao(client: AsyncClient):
    response = await client.post(PRODUTOS_URL, json={})

    assert response.status_code == 401

async def test_nao_permite_nome_de_produto_duplicado(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)

    primeiro = build_produto_payload(categoria_id, unidade_id, 3)
    segundo = build_produto_payload(categoria_id, unidade_id, 4)

    segundo["nome"] = primeiro["nome"]

    primeira_response = await client.post(PRODUTOS_URL, json=primeiro, headers=auth_headers)
    assert primeira_response.status_code == 201

    segunda_response = await client.post(PRODUTOS_URL, json=segundo, headers=auth_headers)
    assert segunda_response.status_code == 409

async def test_nao_permite_codigo_de_produto_duplicado(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)

    primeiro = build_produto_payload(categoria_id, unidade_id, 5)
    segundo = build_produto_payload(categoria_id, unidade_id, 6)

    segundo["cod_idt"] = primeiro["cod_idt"]

    primeira_response = await client.post(PRODUTOS_URL, json=primeiro, headers=auth_headers)
    assert primeira_response.status_code == 201

    segunda_response = await client.post(PRODUTOS_URL, json=segundo, headers=auth_headers)
    assert segunda_response.status_code == 409

async def test_preco_do_produto_nao_pode_ser_negativo(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)

    payload = build_produto_payload(categoria_id=categoria_id, unidade_medida_id=unidade_id, indice=7)
    payload["preco_venda_atual"] = "-1.00"

    response = await client.post(PRODUTOS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 422

async def test_categoria_do_produto_deve_existir(client: AsyncClient, auth_headers: dict):
    _, unidade_id = await criar_catalogo_base(client, auth_headers)

    payload = build_produto_payload(categoria_id=99999, unidade_medida_id=unidade_id, indice=8)

    response = await client.post(PRODUTOS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 404

async def test_unidade_do_produto_deve_existir(client: AsyncClient, auth_headers: dict):
    categoria_id, _ = await criar_catalogo_base(client, auth_headers)

    payload = build_produto_payload(categoria_id=categoria_id, unidade_medida_id=99999, indice=9)

    response = await client.post(PRODUTOS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 404

async def test_listar_produtos(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)

    for indice in [10, 11, 12]:
        response = await client.post(PRODUTOS_URL, json=build_produto_payload(categoria_id, unidade_id, indice), headers=auth_headers)
        assert response.status_code == 201
    
    response = await client.get(PRODUTOS_URL, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert body["page"] == 1
    assert body["per_page"] == 20
    assert len(body["items"]) == 3

async def test_produto_sem_estoque_possui_status_sem_estoque(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)

    create_response = await client.post(PRODUTOS_URL, json=build_produto_payload(categoria_id, unidade_id, 13), headers=auth_headers)
    assert create_response.status_code == 201

    response = await client.get(PRODUTOS_URL, headers=auth_headers, params={"nome": "Produto Teste 13"})
    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1

    produto = body["items"][0]
    
    assert produto["status"] == "SEM_ESTOQUE"
    assert Decimal(str(produto["estoque_total"])) == Decimal("0")

async def test_filtrar_produto_por_nome(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)

    for indice in [14, 15]:
        response = await client.post(PRODUTOS_URL, json=build_produto_payload(categoria_id, unidade_id, indice), headers=auth_headers)
        assert response.status_code == 201

    response = await client.get(PRODUTOS_URL, params={"nome": "Produto Teste 15"}, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["nome"] == "Produto Teste 15"

async def test_filtrar_produto_por_categoria(client: AsyncClient, auth_headers: dict):
    categoria_1 = await client.post(CATEGORIAS_URL, json={"nome": "Bebidas"}, headers=auth_headers)
    categoria_2 = await client.post(CATEGORIAS_URL, json={"nome": "Padaria"}, headers=auth_headers)

    unidade = await client.post(UNIDADES_URL, json={"nome": "Unidade", "sigla": "un"}, headers=auth_headers)

    assert categoria_1.status_code == 201
    assert categoria_2.status_code == 201
    assert unidade.status_code == 201

    categoria_1_id = categoria_1.json()["id"]
    categoria_2_id = categoria_2.json()["id"]

    unidade_id = unidade.json()["id"]

    response_1 = await client.post(PRODUTOS_URL, json=build_produto_payload(categoria_1_id, unidade_id, 16), headers=auth_headers)
    response_2 = await client.post(PRODUTOS_URL, json=build_produto_payload(categoria_2_id, unidade_id, 17), headers=auth_headers)

    assert response_1.status_code == 201
    assert response_2.status_code == 201

    response = await client.get(PRODUTOS_URL, params={"categoria_id": categoria_2_id}, headers=auth_headers)

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["id"] == response_2.json()["id"]

async def test_filtrar_produto_por_intervalo_de_preco(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)

    barato = build_produto_payload(categoria_id, unidade_id, 18)

    barato["preco_venda_atual"] = "5.00"

    caro = build_produto_payload(categoria_id, unidade_id, 19)

    caro["preco_venda_atual"] = "50.00"

    response_barato = await client.post(PRODUTOS_URL, json=barato, headers=auth_headers)
    response_caro = await client.post(PRODUTOS_URL, json=caro, headers=auth_headers)

    assert response_barato.status_code == 201
    assert response_caro.status_code == 201

    response = await client.get(PRODUTOS_URL, params={"preco_min": "40.00", "preco_max": "60.00"}, headers=auth_headers)

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["nome"] == caro["nome"]

async def test_buscar_produto_por_id(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)
    payload = build_produto_payload(categoria_id, unidade_id, 20)
    create_response = await client.post(PRODUTOS_URL, json=payload, headers=auth_headers)
    assert create_response.status_code == 201

    produto_id = create_response.json()["id"]
    response = await client.get(f"{PRODUTOS_URL}{produto_id}", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["id"] == produto_id
    assert body["nome"] == payload["nome"]
    assert body["categoria_id"] == categoria_id
    assert body["unidade_medida_id"] == unidade_id
    assert body["lotes"] == []
    assert body["estoques"] == []

async def test_buscar_produto_inexistente(client: AsyncClient, auth_headers: dict):
    response = await client.get(f"{PRODUTOS_URL}/999999", headers=auth_headers)

    assert response.status_code == 404

async def test_editar_produto(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)

    create_response = await client.post(PRODUTOS_URL, json=build_produto_payload(categoria_id, unidade_id, 21), headers=auth_headers)

    assert create_response.status_code == 201

    produto_id = create_response.json()["id"]

    response = await client.patch(f"{PRODUTOS_URL}{produto_id}", json={"nome": "Produto Atualizado", "descricao": "Descrição atualizada", "preco_venda_atual": "19.90"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    body = response.json()

    assert body["nome"] == "Produto Atualizado"
    assert body["descricao"] == "Descrição atualizada"
    assert Decimal(str(body["preco_venda_atual"])) == Decimal("19.90")


async def test_nao_permite_editar_produto_para_nome_duplicado(client: AsyncClient, auth_headers: dict):
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers)

    primeiro = await client.post(PRODUTOS_URL, json=build_produto_payload(categoria_id, unidade_id, 22), headers=auth_headers)

    segundo = await client.post(PRODUTOS_URL, json=build_produto_payload(categoria_id, unidade_id, 23), headers=auth_headers)

    assert primeiro.status_code == 201
    assert segundo.status_code == 201

    response = await client.patch(
        f"{PRODUTOS_URL}{segundo.json()['id']}",
        json={"nome": primeiro.json()["nome"]},
        headers=auth_headers,
    )

    assert response.status_code == 409


async def test_listagem_de_produtos_exige_autenticacao(client: AsyncClient):
    response = await client.get(PRODUTOS_URL)

    assert response.status_code == 401