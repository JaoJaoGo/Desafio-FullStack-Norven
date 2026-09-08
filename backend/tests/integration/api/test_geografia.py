from httpx import AsyncClient

from core.configs import settings

GEOGRAFIA_URL = f"{settings.API_V1_STR}/geografia"


async def _buscar_pais_com_estado(client: AsyncClient, auth_headers: dict) -> tuple[list[dict], list[dict]]:
    paises_response = await client.get(f"{GEOGRAFIA_URL}/paises", headers=auth_headers)

    for pais in paises_response.json():
        estados_response = await client.get(
            f"{GEOGRAFIA_URL}/estados",
            params={"pais_id": pais["id"]},
            headers=auth_headers,
        )
        estados = estados_response.json()
        if estados:
            return paises_response.json(), estados

    raise AssertionError("O seed geográfico não possui país com estados.")


async def test_listar_paises_retorna_catalogo_populado(client: AsyncClient, auth_headers: dict):
    response = await client.get(f"{GEOGRAFIA_URL}/paises", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()

    assert body
    assert all({"id", "nome", "nome_pt", "sigla", "ddi"} <= set(pais) for pais in body)


async def test_listar_estados_filtra_pelo_pais(client: AsyncClient, auth_headers: dict):
    paises, estados_esperados = await _buscar_pais_com_estado(client, auth_headers)
    pais_id = next(pais["id"] for pais in paises if pais["id"] == estados_esperados[0]["pais_id"])

    response = await client.get(f"{GEOGRAFIA_URL}/estados", params={"pais_id": pais_id}, headers=auth_headers)

    assert response.status_code == 200
    estados = response.json()
    assert estados
    assert len(estados) == len(estados_esperados)
    assert all(estado["pais_id"] == pais_id for estado in estados)


async def test_listar_cidades_filtra_pelo_estado(client: AsyncClient, auth_headers: dict):
    _, estados = await _buscar_pais_com_estado(client, auth_headers)
    estado_id = estados[0]["id"]

    response = await client.get(f"{GEOGRAFIA_URL}/cidades", params={"estado_id": estado_id}, headers=auth_headers)

    assert response.status_code == 200
    cidades = response.json()
    assert cidades
    assert all(cidade["estado_id"] == estado_id for cidade in cidades)


async def test_buscar_hierarquia_de_cidade(client: AsyncClient, auth_headers: dict):
    _, estados = await _buscar_pais_com_estado(client, auth_headers)
    estado_id = estados[0]["id"]
    cidades_response = await client.get(f"{GEOGRAFIA_URL}/cidades", params={"estado_id": estado_id}, headers=auth_headers)
    cidade_id = cidades_response.json()[0]["id"]

    response = await client.get(f"{GEOGRAFIA_URL}/cidades/{cidade_id}/hierarquia", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["cidade"]["id"] == cidade_id
    assert body["cidade"]["estado_id"] == body["estado"]["id"]
    assert body["estado"]["pais_id"] == body["pais"]["id"]


async def test_hierarquia_de_cidade_inexistente_retorna_404(client: AsyncClient, auth_headers: dict):
    response = await client.get(f"{GEOGRAFIA_URL}/cidades/999999/hierarquia", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Cidade ou hierarquia geográfica não encontrada."


async def test_parametros_geograficos_devem_ser_positivos(client: AsyncClient, auth_headers: dict):
    estados_response = await client.get(f"{GEOGRAFIA_URL}/estados", params={"pais_id": 0}, headers=auth_headers)
    cidades_response = await client.get(f"{GEOGRAFIA_URL}/cidades", params={"estado_id": 0}, headers=auth_headers)

    assert estados_response.status_code == 422
    assert cidades_response.status_code == 422


async def test_rotas_geograficas_exigem_autenticacao(client: AsyncClient):
    paises_response = await client.get(f"{GEOGRAFIA_URL}/paises")
    estados_response = await client.get(f"{GEOGRAFIA_URL}/estados", params={"pais_id": 1})
    cidades_response = await client.get(f"{GEOGRAFIA_URL}/cidades", params={"estado_id": 1})
    hierarquia_response = await client.get(f"{GEOGRAFIA_URL}/cidades/1/hierarquia")

    assert paises_response.status_code == 401
    assert estados_response.status_code == 401
    assert cidades_response.status_code == 401
    assert hierarquia_response.status_code == 401
