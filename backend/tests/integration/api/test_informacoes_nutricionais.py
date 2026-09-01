from httpx import AsyncClient

from core.configs import settings
from tests.integration.api.payloads import build_informacao_nutricional_payload

CATEGORIAS_URL = f"{settings.API_V1_STR}/categorias/"
UNIDADES_URL = f"{settings.API_V1_STR}/unidades-medidas/"
PRODUTOS_URL = f"{settings.API_V1_STR}/produtos/"

async def criar_categoria(client: AsyncClient, auth_headers: dict) -> int:
    response = await client.post(CATEGORIAS_URL, json={"nome": "Cereais"}, headers=auth_headers)

    assert response.status_code == 201

    return response.json()["id"]

async def criar_unidade(client: AsyncClient, auth_headers: dict) -> int:
    response = await client.post(UNIDADES_URL, json={"nome": "Grama", "sigla": "g"}, headers=auth_headers)

    assert response.status_code == 201

    return response.json()["id"]

def build_produto_payload(categoria_id: int, unidade_id: int, indice: int, informacao_nutricional: dict | None) -> dict:
    return {
        "cod_idt": f"PROD-NUT-{indice:03d}",
        "nome": f"Produto Nutricional {indice}",
        "descricao": "Produto criado pelos testes.",
        "preco_venda_atual": "12.50",
        "eh_perecivel": False,
        "categoria_id": categoria_id,
        "unidade_medida_id": unidade_id,
        "informacao_nutricional": informacao_nutricional,
    }

async def test_criar_informacao_nutricional_junto_com_produto(client: AsyncClient, auth_headers: dict):
    categoria_id = await criar_categoria(client, auth_headers)
    unidade_id = await criar_unidade(client, auth_headers)
    informacao = build_informacao_nutricional_payload(unidade_id)
    payload = build_produto_payload(categoria_id, unidade_id, 1, informacao)

    response = await client.post(PRODUTOS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 201

    body = response.json()
    assert body["informacao_nutricional_id"] is not None

    nutricional = body["informacao_nutricional"]
    assert nutricional is not None
    assert nutricional["porcao_quantidade"] == "100.00"
    assert nutricional["valor_energetico_kcal"] == "250.00"
    assert nutricional["carboidratos_g"] == "35.00"
    assert nutricional["proteinas_g"] == "10.00"
    assert nutricional["gorduras_totais_g"] == "8.00"
    assert nutricional["unidade_porcao_id"] == unidade_id

async def test_reutiliza_informacao_nutricional_identica(client: AsyncClient, auth_headers: dict):
    categoria_id = await criar_categoria(client, auth_headers)
    unidade_id = await criar_unidade(client, auth_headers)
    informacao = build_informacao_nutricional_payload(unidade_id)

    primeiro_payload = build_produto_payload(categoria_id, unidade_id, 2, informacao)
    segundo_payload = build_produto_payload(categoria_id, unidade_id, 3, informacao.copy())

    primeira_response = await client.post(PRODUTOS_URL, json=primeiro_payload, headers=auth_headers)
    assert primeira_response.status_code == 201

    segunda_response = await client.post(PRODUTOS_URL, json=segundo_payload, headers=auth_headers)
    assert segunda_response.status_code == 201

    primeira_info_id = primeira_response.json()["informacao_nutricional_id"]
    segunda_info_id = segunda_response.json()["informacao_nutricional_id"]

    assert primeira_info_id == segunda_info_id

async def test_porcao_deve_ser_maior_que_zero(client: AsyncClient, auth_headers: dict):
    categoria_id = await criar_categoria(client, auth_headers)
    unidade_id = await criar_unidade(client, auth_headers)
    informacao = build_informacao_nutricional_payload(unidade_id)
    informacao["porcao_quantidade"] = "0.00"

    payload = build_produto_payload(categoria_id, unidade_id, 4, informacao)

    response = await client.post(PRODUTOS_URL, json=payload, headers=auth_headers)

    assert response.status_code == 422

async def test_nutrientes_nao_podem_ser_negativos(client: AsyncClient, auth_headers: dict):
    categoria_id = await criar_categoria(client, auth_headers)
    unidade_id = await criar_unidade(client, auth_headers)
    informacao = build_informacao_nutricional_payload(unidade_id)
    informacao["proteinas_g"] = "-1.00"

    payload = build_produto_payload(categoria_id, unidade_id, 5, informacao)

    response = await client.post(PRODUTOS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 422

async def test_unidade_da_porcao_deve_existir(client: AsyncClient, auth_headers: dict):
    categoria_id = await criar_categoria(client, auth_headers)
    unidade_id = await criar_unidade(client, auth_headers)
    informacao = build_informacao_nutricional_payload(999999)
    payload = build_produto_payload(categoria_id, unidade_id, 6, informacao)

    response = await client.post(PRODUTOS_URL, json=payload, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Unidade de medida não encontrada"

async def test_atualizar_informacao_nutricional_do_produto(client: AsyncClient, auth_headers: dict):
    categoria_id = await criar_categoria(client, auth_headers)
    unidade_id = await criar_unidade(client, auth_headers)
    informacao_original = build_informacao_nutricional_payload(unidade_id)

    payload = build_produto_payload(categoria_id, unidade_id, 7, informacao_original)

    create_response = await client.post(PRODUTOS_URL, json=payload, headers=auth_headers)
    assert create_response.status_code == 201

    produto_id = create_response.json()["id"]
    info_id_anterior = create_response.json()["informacao_nutricional_id"]
    nova_informacao = build_informacao_nutricional_payload(unidade_id)
    nova_informacao["valor_energetico_kcal"] = "300.00"

    response = await client.patch(f"{PRODUTOS_URL}{produto_id}", json={"informacao_nutricional": nova_informacao}, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["informacao_nutricional_id"] != info_id_anterior
    assert body["informacao_nutricional"]["valor_energetico_kcal"] == "300.00"

async def test_remover_informacao_nutricional_do_produto(client: AsyncClient, auth_headers: dict):
    categoria_id = await criar_categoria(client, auth_headers)
    unidade_id = await criar_unidade(client, auth_headers)
    informacao = build_informacao_nutricional_payload(unidade_id)

    payload = build_produto_payload(categoria_id, unidade_id, 8, informacao)

    create_response = await client.post(PRODUTOS_URL, json=payload, headers=auth_headers)
    assert create_response.status_code == 201

    produto_id = create_response.json()["id"]

    response = await client.patch(f"{PRODUTOS_URL}{produto_id}", json={"informacao_nutricional": None}, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["informacao_nutricional_id"] is None
    assert body["informacao_nutricional"] is None