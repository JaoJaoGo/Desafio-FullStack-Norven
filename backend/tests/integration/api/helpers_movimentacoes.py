from datetime import date, timedelta
from decimal import Decimal

from httpx import AsyncClient

from core.configs import settings

from tests.integration.api.payloads import build_entrada_payload, build_fornecedor_payload, build_lote_payload, build_produto_payload

CATEGORIAS_URL = f"{settings.API_V1_STR}/categorias/"
UNIDADES_URL = f"{settings.API_V1_STR}/unidades-medidas/"
FORNECEDORES_URL = f"{settings.API_V1_STR}/fornecedores/"
PRODUTOS_URL = f"{settings.API_V1_STR}/produtos/"
LOTES_URL = f"{settings.API_V1_STR}/lotes/"
ENTRADAS_URL = f"{settings.API_V1_STR}/entradas/"
ESTOQUES_URL = f"{settings.API_V1_STR}/estoques/"
SAIDAS_URL = f"{settings.API_V1_STR}/saidas/"

async def criar_catalogo_base(client: AsyncClient, auth_headers: dict, indice: int) -> tuple[int, int]:
    categoria_response = await client.post(CATEGORIAS_URL, json={"nome": f"Categoria Movimento {indice}"}, headers=auth_headers)
    assert categoria_response.status_code == 201

    unidade_response = await client.post(UNIDADES_URL, json={"nome": f"Unidade Movimento {indice}", "sigla": f"u{indice}"}, headers=auth_headers)
    assert unidade_response.status_code == 201

    return (
        categoria_response.json()["id"],
        unidade_response.json()["id"],
    )

async def criar_fornecedor(client: AsyncClient, auth_headers: dict, municipio_id: int, indice: int) -> dict:
    response = await client.post(FORNECEDORES_URL, json=build_fornecedor_payload(municipio_id, indice), headers=auth_headers)
    assert response.status_code == 201

    return response.json()


async def criar_produto(client: AsyncClient, auth_headers: dict, categoria_id: int, unidade_id: int, indice: int, eh_perecivel: bool = True) -> dict:
    response = await client.post(
        PRODUTOS_URL,
        json=build_produto_payload(categoria_id=categoria_id, unidade_medida_id=unidade_id, indice=indice, eh_perecivel=eh_perecivel),
        headers=auth_headers
    )
    assert response.status_code == 201

    return response.json()

async def criar_lote(client: AsyncClient, auth_headers: dict, produto_id: int, indice: int, eh_perecivel: bool = True) -> dict:
    validade = None

    if eh_perecivel:
        validade = date.today() + timedelta(days=180)

    response = await client.post(LOTES_URL, json=build_lote_payload(produto_id=produto_id, indice=indice, data_validade=validade), headers=auth_headers)
    assert response.status_code == 201

    return response.json()

async def criar_cenario_movimentacao(client: AsyncClient, auth_headers: dict, municipio_id: int, indice: int = 1, eh_perecivel: bool = True) -> dict:
    categoria_id, unidade_id = await criar_catalogo_base(client, auth_headers, indice)
    fornecedor = await criar_fornecedor(client, auth_headers, municipio_id, indice)
    produto = await criar_produto(client, auth_headers, categoria_id, unidade_id, indice, eh_perecivel)
    lote = await criar_lote(client, auth_headers, produto["id"], indice, eh_perecivel)

    return {
        "categoria_id": categoria_id,
        "unidade_id": unidade_id,
        "fornecedor": fornecedor,
        "produto": produto,
        "lote": lote,
    }

async def criar_entrada(
    client: AsyncClient,
    auth_headers: dict,
    cenario: dict,
    indice: int = 1,
    quantidade: str = "10.000",
    preco_custo_unitario: str = "5.50",
    tipo_entrada: str = "COMPRA",
    data_entrada=None,
) -> dict:
    response = await client.post(
        ENTRADAS_URL,
        json=build_entrada_payload(
            produto_id=cenario["produto"]["id"],
            fornecedor_id=cenario["fornecedor"]["id"],
            lote_id=cenario["lote"]["id"],
            indice=indice,
            quantidade=quantidade,
            preco_custo_unitario=preco_custo_unitario,
            tipo_entrada=tipo_entrada,
            data_entrada=data_entrada,
        ),
        headers=auth_headers,
    )
    assert response.status_code == 201

    return response.json()

def decimal_json(value) -> Decimal:
    return Decimal(str(value))