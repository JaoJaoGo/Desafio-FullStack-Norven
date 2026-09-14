from sqlalchemy.engine.result import Result
from sqlalchemy.sql.selectable import Select
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from seeders.bootstrap import SRC_DIR  # noqa: F401
from seeders.helpers.seeder_helpers import get_city_map
from core.enums import NivelAcessoEnum
from core.security import get_password_hash
from models.contato_model import ContatoModel
from models.endereco_model import EnderecoModel
from models.usuario_model import UsuarioModel

SEED_USER_PASSWORD = "Norven@123"

USUARIOS = [
    ("Ana Souza", "ana.souza@norven.com.br", NivelAcessoEnum.ADMINISTRADOR, ("Goiânia", "GO"), "Rua 1", "120", "Setor Oeste", "74110-010", "62", "991000001"),
    ("Bruno Lima", "bruno.lima@norven.com.br", NivelAcessoEnum.ADMINISTRADOR, ("Goiânia", "GO"), "Rua 2", "215", "Setor Bueno", "74230-020", "62", "991000002"),
    ("Carla Mendes", "carla.mendes@norven.com.br", NivelAcessoEnum.OPERADOR, ("Aparecida de Goiânia", "GO"), "Avenida Rio Verde", "310", "Vila Brasília", "74905-030", "62", "991000003"),
    ("Diego Alves", "diego.alves@norven.com.br", NivelAcessoEnum.OPERADOR, ("Goiânia", "GO"), "Rua T-30", "440", "Setor Bueno", "74210-040", "62", "991000004"),
    ("Eduarda Rocha", "eduarda.rocha@norven.com.br", NivelAcessoEnum.OPERADOR, ("Anápolis", "GO"), "Avenida Brasil", "520", "Centro", "75020-050", "62", "991000005"),
    ("Felipe Costa", "felipe.costa@norven.com.br", NivelAcessoEnum.OPERADOR, ("Goiânia", "GO"), "Rua 90", "610", "Setor Sul", "74093-060", "62", "991000006"),
    ("Gabriela Nunes", "gabriela.nunes@norven.com.br", NivelAcessoEnum.OPERADOR, ("Aparecida de Goiânia", "GO"), "Rua Independência", "705", "Centro", "74980-070", "62", "991000007"),
    ("Henrique Martins", "henrique.martins@norven.com.br", NivelAcessoEnum.OPERADOR, ("Goiânia", "GO"), "Rua 10", "810", "Setor Central", "74020-080", "62", "991000008"),
    ("Isabela Freitas", "isabela.freitas@norven.com.br", NivelAcessoEnum.OPERADOR, ("Anápolis", "GO"), "Rua Engenheiro Portela", "915", "Jundiaí", "75110-090", "62", "991000009"),
    ("João Ribeiro", "joao.ribeiro@norven.com.br", NivelAcessoEnum.OPERADOR, ("Goiânia", "GO"), "Avenida T-4", "1020", "Setor Bueno", "74230-100", "62", "991000010"),
    ("Larissa Campos", "larissa.campos@norven.com.br", NivelAcessoEnum.OPERADOR, ("Goiânia", "GO"), "Rua 85", "1115", "Setor Marista", "74160-110", "62", "991000011"),
    ("Marcos Vieira", "marcos.vieira@norven.com.br", NivelAcessoEnum.OPERADOR, ("Aparecida de Goiânia", "GO"), "Avenida Igualdade", "1210", "Garavelo", "74350-120", "62", "991000012"),
]

async def _find_or_create_contact(session: AsyncSession, ddd: str, numero: str) -> ContatoModel:
    query: Select[tuple[ContatoModel]] = select(ContatoModel).where(
        ContatoModel.cod_pais == "55",
        ContatoModel.ddd == ddd,
        ContatoModel.numero == numero,
    )

    result: Result[tuple[ContatoModel]] = await session.execute(query)
    contato: ContatoModel | None = result.scalar_one_or_none()

    if contato is None:
        contato = ContatoModel(
            cod_pais="55",
            ddd=ddd,
            numero=numero,
        )
        session.add(contato)
        await session.flush()

    return contato

async def seed_usuarios(session: AsyncSession) -> dict[str, UsuarioModel]:
    print("Seeding funcionários de teste...")

    city_map: dict[tuple[str, str], int] = await get_city_map(session, {item[3] for item in USUARIOS})

    result: dict[str, UsuarioModel] = {}

    for item in USUARIOS:
        (
            nome,
            email,
            nivel_acesso,
            cidade,
            logradouro,
            numero_endereco,
            bairro,
            cep,
            ddd,
            telefone,
        ) = item

        legacy_email: str = email.replace("@norven.com.br", "@norven.test")

        query: Select[tuple[UsuarioModel]] = select(UsuarioModel).where(UsuarioModel.email.in_([email, legacy_email]))

        query_result: Result[tuple[UsuarioModel]] = await session.execute(query)
        usuario: UsuarioModel | None = query_result.scalar_one_or_none()

        if usuario is None:
            endereco: EnderecoModel | None = EnderecoModel(
                logradouro=logradouro,
                numero=numero_endereco,
                complemento=None,
                cep=cep,
                bairro=bairro,
                municipio_id=city_map[cidade],
            )

            session.add(endereco)
            await session.flush()

            contato: ContatoModel | None = await _find_or_create_contact(
                session,
                ddd,
                telefone,
            )

            usuario: UsuarioModel | None = UsuarioModel(
                nome=nome,
                email=email,
                password=get_password_hash(SEED_USER_PASSWORD),
                nivel_acesso=nivel_acesso,
                endereco_id=endereco.id,
                contato_id=contato.id,
            )

            session.add(usuario)
            await session.flush()
        else:
            usuario.nome = nome
            usuario.email = email
            usuario.password = get_password_hash(SEED_USER_PASSWORD)
            usuario.nivel_acesso = nivel_acesso

            endereco: EnderecoModel | None = await session.get(EnderecoModel, usuario.endereco_id)

            if endereco is not None:
                endereco.logradouro = logradouro
                endereco.numero = numero_endereco
                endereco.complemento = None
                endereco.cep = cep
                endereco.bairro = bairro
                endereco.municipio_id = city_map[cidade]

            contato: ContatoModel | None = await session.get(ContatoModel, usuario.contato_id)

            if contato is not None:
                contato.cod_pais = "55"
                contato.ddd = ddd
                contato.numero = telefone

            await session.flush()

        result[email] = usuario

    return result