from sqlalchemy.engine.result import Result
from sqlalchemy.sql.selectable import Select
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from seeders.bootstrap import SRC_DIR  # noqa: F401
from seeders.helpers.seeder_helpers import get_city_map

from models.contato_model import ContatoModel
from models.endereco_model import EnderecoModel
from models.fornecedor_model import FornecedorModel

FORNECEDORES = [
    ("Distribuidora Cerrado", "10000000000001", ("Goiânia", "GO"), "Avenida Anhanguera", "1000", "Setor Central", "74043-010", "62", "992000001"),
    ("Alimentos Goiás", "10000000000002", ("Goiânia", "GO"), "Avenida Goiás", "1100", "Setor Central", "74005-020", "62", "992000002"),
    ("Laticínios Bela Vista", "10000000000003", ("Aparecida de Goiânia", "GO"), "Avenida Independência", "1200", "Centro", "74980-030", "62", "992000003"),
    ("Carnes Premium Centro-Oeste", "10000000000004", ("Goiânia", "GO"), "Avenida Perimetral", "1300", "Setor Campinas", "74525-040", "62", "992000004"),
    ("Hortifruti Primavera", "10000000000005", ("Anápolis", "GO"), "Avenida Universitária", "1400", "Vila Santa Isabel", "75083-050", "62", "992000005"),
    ("Panificação Brasil", "10000000000006", ("Goiânia", "GO"), "Rua 44", "1500", "Setor Norte Ferroviário", "74063-060", "62", "992000006"),
    ("Congelados Polar", "10000000000007", ("Aparecida de Goiânia", "GO"), "Avenida São Paulo", "1600", "Vila Brasília", "74905-070", "62", "992000007"),
    ("Higiene Mais", "10000000000008", ("Goiânia", "GO"), "Avenida 85", "1700", "Setor Marista", "74160-080", "62", "992000008"),
    ("Limpeza Total", "10000000000009", ("Goiânia", "GO"), "Avenida T-63", "1800", "Setor Bueno", "74230-090", "62", "992000009"),
    ("Bebidas Planalto", "10000000000010", ("Anápolis", "GO"), "Avenida Fernando Costa", "1900", "Jundiaí", "75110-100", "62", "992000010"),
    ("Atacado Boa Compra", "10000000000011", ("Goiânia", "GO"), "Avenida Castelo Branco", "2000", "Setor Coimbra", "74530-110", "62", "992000011"),
    ("Mercearia Distribuições", "10000000000012", ("Aparecida de Goiânia", "GO"), "Avenida das Nações", "2100", "Garavelo", "74350-120", "62", "992000012"),
]

async def seed_fornecedores(session: AsyncSession) -> dict[str, FornecedorModel]:
    print("Seeding fornecedores...")

    city_map: dict[tuple[str, str], int] = await get_city_map(session, {item[2] for item in FORNECEDORES})
    result: dict[str, FornecedorModel] = {}

    for item in FORNECEDORES:
        (
            nome,
            cnpj,
            cidade,
            logradouro,
            numero_endereco,
            bairro,
            cep,
            ddd,
            telefone,
        ) = item

        query: Select[tuple[FornecedorModel]] = select(FornecedorModel).where(FornecedorModel.cnpj == cnpj)

        query_result: Result[tuple[FornecedorModel]] = await session.execute(query)
        fornecedor: FornecedorModel | None = query_result.scalar_one_or_none()

        if fornecedor is None:
            endereco: EnderecoModel | None = EnderecoModel(
                logradouro=logradouro,
                numero=numero_endereco,
                complemento=None,
                cep=cep,
                bairro=bairro,
                municipio_id=city_map[cidade],
            )

            contato: ContatoModel | None = ContatoModel(
                cod_pais="55",
                ddd=ddd,
                numero=telefone,
            )

            session.add_all([endereco, contato])
            await session.flush()

            fornecedor = FornecedorModel(
                nome=nome,
                cnpj=cnpj,
                endereco_id=endereco.id,
                contato_id=contato.id,
            )

            session.add(fornecedor)
            await session.flush()
        else:
            fornecedor.nome = nome
            endereco: EnderecoModel | None = await session.get(EnderecoModel, fornecedor.endereco_id)

            if endereco is not None:
                endereco.logradouro = logradouro
                endereco.numero = numero_endereco
                endereco.complemento = None
                endereco.cep = cep
                endereco.bairro = bairro
                endereco.municipio_id = city_map[cidade]

            contato: ContatoModel | None = await session.get(ContatoModel, fornecedor.contato_id)

            if contato is not None:
                contato.cod_pais = "55"
                contato.ddd = ddd
                contato.numero = telefone

            await session.flush()

        result[cnpj] = fornecedor

    return result
