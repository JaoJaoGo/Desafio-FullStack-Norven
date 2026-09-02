from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.configs import settings
from core.enums import NivelAcessoEnum
from core.security import get_password_hash
from models.cidade_model import CidadeModel
from models.estado_model import EstadoModel
from models.contato_model import ContatoModel
from models.endereco_model import EnderecoModel
from models.usuario_model import UsuarioModel

ADMIN_EMAIL = "admin@norven.com.br"

async def seed_admin(session: AsyncSession) -> None:
    query_admin = select(UsuarioModel).where(UsuarioModel.email == ADMIN_EMAIL)

    result_admin = await session.execute(query_admin)
    admin_existente = result_admin.scalar_one_or_none()

    if admin_existente:
        admin_existente.password = get_password_hash(settings.PRIMARY_ADMIN_PASSWORD)

        await session.flush()

        print("Usuário administrador já cadastrado. Senha sincronizada com a configuração atual."
        )

        return

    query_goiania = (
        select(CidadeModel)
        .join(EstadoModel, CidadeModel.estado_id == EstadoModel.id)
        .where(CidadeModel.nome == "Goiânia", EstadoModel.uf == "GO")
    )

    result_goiania = await session.execute(query_goiania)
    goiania = result_goiania.scalar_one_or_none()

    if goiania is None:
        raise RuntimeError(
            "Goiânia/GO não foi encontrada. Execute o GeographySeeder antes do AdminSeeder."
        )

    endereco = EnderecoModel(
        logradouro="Rua de Teste",
        numero="100",
        complemento="Sala 1",
        cep="74000-000",
        bairro="Setor Central",
        municipio_id=goiania.id,
    )

    session.add(endereco)
    await session.flush()

    contato = ContatoModel(
        cod_pais="55",
        ddd="62",
        numero="999999999",
    )

    session.add(contato)
    await session.flush()

    admin = UsuarioModel(
        nome="Administrador",
        email=ADMIN_EMAIL,
        password=get_password_hash(
            settings.PRIMARY_ADMIN_PASSWORD
        ),
        nivel_acesso=NivelAcessoEnum.ADMINISTRADOR,
        endereco_id=endereco.id,
        contato_id=contato.id,
    )

    session.add(admin)
    await session.flush()

    print(f"Administrador criado com sucesso: {ADMIN_EMAIL}")