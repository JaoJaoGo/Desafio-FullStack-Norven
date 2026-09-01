from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.configs import settings
from models.contato_model import ContatoModel

from tests.integration.api.payloads import build_usuario_payload

USUARIOS_URL = f"{settings.API_V1_STR}/usuarios/"

async def test_contato_e_criado_junto_com_usuario(client: AsyncClient, auth_headers: dict, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 30)

    create_response = await client.post(USUARIOS_URL, json=payload)
    assert create_response.status_code == 201

    usuario_id = create_response.json()["id"]

    response = await client.get(f"{USUARIOS_URL}{usuario_id}", headers=auth_headers)
    assert response.status_code == 200

    contato = response.json()["contato"]
    assert contato["id"] is not None
    assert contato["cod_pais"] == payload["contato"]["cod_pais"]
    assert contato["ddd"] == payload["contato"]["ddd"]
    assert contato["numero"] == payload["contato"]["numero"]

async def test_atualizar_contato_do_usuario(client: AsyncClient, auth_headers: dict, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 31)

    create_response = await client.post(USUARIOS_URL, json=payload)
    assert create_response.status_code == 201

    usuario_id = create_response.json()["id"]
    contato_id_anterior = create_response.json()["contato_id"]

    response = await client.patch(f"{USUARIOS_URL}{usuario_id}", json={"contato": {"numero": "999999999"}}, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["contato"]["numero"] == "999999999"

    # Campos não enviados devem continuar iguais.
    assert body["contato"]["cod_pais"] == payload["contato"]["cod_pais"]
    assert body["contato"]["ddd"] == payload["contato"]["ddd"]
    assert body["contato_id"] != contato_id_anterior

async def test_contato_anterior_e_preservado_apos_edicao(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 32)

    create_response = await client.post(USUARIOS_URL, json=payload)
    assert create_response.status_code == 201

    usuario_id = create_response.json()["id"]
    contato_id_anterior = create_response.json()["contato_id"]

    update_response = await client.patch(f"{USUARIOS_URL}{usuario_id}", json={"contato": {"numero": "988888888"}}, headers=auth_headers)
    assert update_response.status_code == 200

    contato_anterior = await db_session.get(ContatoModel, contato_id_anterior)
    assert contato_anterior is not None
    assert contato_anterior.numero == payload["contato"]["numero"]

async def test_nao_permite_contato_duplicado(client: AsyncClient, municipio_id: int):
    primeiro = build_usuario_payload(municipio_id, 33)
    segundo = build_usuario_payload(municipio_id, 34)

    segundo["contato"] = primeiro["contato"].copy()

    primeira_response = await client.post(USUARIOS_URL, json=primeiro)
    assert primeira_response.status_code == 201

    segunda_response = await client.post(USUARIOS_URL, json=segundo)
    assert segunda_response.status_code == 409

async def test_contato_incompleto_retorna_erro_de_validacao(client: AsyncClient, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 35)
    payload["contato"].pop("numero")

    response = await client.post(USUARIOS_URL, json=payload)

    assert response.status_code == 422