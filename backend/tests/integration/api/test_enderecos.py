from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.configs import settings
from models.endereco_model import EnderecoModel

from tests.integration.api.payloads import build_usuario_payload

USUARIOS_URL = f"{settings.API_V1_STR}/usuarios/"

async def test_endereco_e_criado_junto_com_usuario(client: AsyncClient, auth_headers: dict, municipio_id: int,):
    payload = build_usuario_payload(municipio_id, 20)

    create_response = await client.post(USUARIOS_URL, json=payload)
    assert create_response.status_code == 201

    usuario_id = create_response.json()["id"]

    response = await client.get(f"{USUARIOS_URL}{usuario_id}", headers=auth_headers)
    assert response.status_code == 200

    endereco = response.json()["endereco"]

    assert endereco["id"] is not None
    assert endereco["logradouro"] == payload["endereco"]["logradouro"]
    assert endereco["numero"] == payload["endereco"]["numero"]
    assert endereco["complemento"] == payload["endereco"]["complemento"]
    assert endereco["cep"] == payload["endereco"]["cep"]
    assert endereco["bairro"] == payload["endereco"]["bairro"]
    assert endereco["municipio_id"] == municipio_id

async def test_atualizar_endereco_do_usuario(client: AsyncClient, auth_headers: dict, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 21)

    create_response = await client.post(USUARIOS_URL, json=payload)
    assert create_response.status_code == 201

    usuario_id = create_response.json()["id"]

    endereco_id_anterior = create_response.json()["endereco_id"]

    response = await client.patch(f"{USUARIOS_URL}{usuario_id}", json={"endereco": {"logradouro": "Avenida Atualizada", "numero": "999"}}, headers=auth_headers)
    assert response.status_code == 200

    body = response.json()

    assert body["endereco"]["logradouro"] == "Avenida Atualizada"
    assert body["endereco"]["numero"] == "999"

    # Campos não enviados são preservados.
    assert body["endereco"]["cep"] == payload["endereco"]["cep"]
    assert body["endereco"]["bairro"] == payload["endereco"]["bairro"]

    # Não alteramos o endereço histórico em-place.
    assert body["endereco_id"] != endereco_id_anterior

async def test_endereco_anterior_e_preservado_apos_edicao(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 22)

    create_response = await client.post(USUARIOS_URL, json=payload)
    assert create_response.status_code == 201

    usuario_id = create_response.json()["id"]

    endereco_id_anterior = create_response.json()["endereco_id"]

    update_response = await client.patch(f"{USUARIOS_URL}{usuario_id}", json={"endereco": {"logradouro": "Rua Endereço Novo"}}, headers=auth_headers)
    assert update_response.status_code == 200

    endereco_anterior = await db_session.get(EnderecoModel, endereco_id_anterior)
    assert endereco_anterior is not None
    assert endereco_anterior.logradouro == payload["endereco"]["logradouro"]

async def test_nao_permite_usuario_com_municipio_inexistente(client: AsyncClient, municipio_id: int):
    payload = build_usuario_payload(municipio_id, 23)
    payload["endereco"]["municipio_id"] = 999999

    response = await client.post(USUARIOS_URL, json=payload)
    assert response.status_code == 409