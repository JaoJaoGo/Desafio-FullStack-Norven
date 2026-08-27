import re
from pathlib import Path
from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

DATA_DIR = Path(__file__).parent / "data"

def _read_copy_data(file_name: str, table_name: str) -> tuple[list[str], list[list[Optional[str]]]]:
    path = DATA_DIR / file_name

    content = path.read_text(
        encoding="utf-8"
    )
    
    pattern = (
        rf"COPY\s+{re.escape(table_name)}\s+"
        rf"\((.*?)\)\s+FROM\s+stdin;\r?\n"
        rf"(.*?)\r?\n\\\."
    )

    match = re.search(
        pattern,
        content,
        re.DOTALL
    )

    if not match:
        raise ValueError(f"Bloco COPY da tabela '{table_name}' não encontrado em {file_name}")
    
    columns = [
        column.strip()
        for column in match.group(1).split(",")
    ]

    rows = []

    for line in match.group(2).splitlines():
        values = []

        for value in line.split("\t"):
            if value == r"\N":
                values.append(None)
            else:
                values.append(value)
        
        rows.append(values)

    return columns, rows

def _to_int(value: Optional[str]) -> Optional[int]:
    if value is None or value == "":
        return None
    
    return int(value)

def _to_point(value: Optional[str]) -> Optional[tuple[float, float]]:
    if value is None or value == "":
        return None

    value = value.strip("()")

    x, y = value.split(",", 1)

    return float(x), float(y)

async def seed_paises(session: AsyncSession) -> None:
    columns, rows = _read_copy_data("paises.sql", "pais")

    records = []

    for row in rows:
        data = dict(zip(columns, row))

        records.append({
            "id": _to_int(data["id"]),
            "nome": data["nome"],
            "nome_pt": data["nome_pt"],
            "sigla": data["sigla"],
            "bacen": _to_int(data["bacen"]),
            "ddi": _to_int(data["ddi"]),
        })

    query = text("""
        INSERT INTO pais (
            id,
            nome,
            nome_pt,
            sigla,
            bacen,
            ddi
        )
        VALUES (
            :id,
            :nome,
            :nome_pt,
            :sigla,
            :bacen,
            :ddi
        )
        ON CONFLICT (id)
        DO UPDATE SET
            nome = EXCLUDED.nome,
            nome_pt = EXCLUDED.nome_pt,
            sigla = EXCLUDED.sigla,
            bacen = EXCLUDED.bacen,
            ddi = EXCLUDED.ddi
    """)

    await session.execute(
        query,
        records
    )

async def seed_estados(session: AsyncSession) -> None:
    columns, rows = _read_copy_data(
        "estado.sql",
        "estado"
    )

    records = []

    for row in rows:
        data = dict(zip(columns, row))

        records.append({
            "id": _to_int(data["id"]),
            "nome": data["nome"],
            "uf": data["uf"],
            "ibge": _to_int(data["ibge"]),
            "pais": _to_int(data["pais"]),
            "ddd": data["ddd"],
        })

    query = text("""
        INSERT INTO estado (
            id,
            nome,
            uf,
            ibge,
            pais,
            ddd
        )
        VALUES (
            :id,
            :nome,
            :uf,
            :ibge,
            :pais,
            CAST(:ddd AS JSON)
        )
        ON CONFLICT (id)
        DO UPDATE SET
            nome = EXCLUDED.nome,
            uf = EXCLUDED.uf,
            ibge = EXCLUDED.ibge,
            pais = EXCLUDED.pais,
            ddd = EXCLUDED.ddd
    """)

    await session.execute(
        query,
        records
    )


async def seed_cidades(session: AsyncSession) -> None:
    columns, rows = _read_copy_data(
        "cidade.sql",
        "cidade"
    )

    records = []

    for row in rows:
        data = dict(zip(columns, row))

        records.append({
            "id": _to_int(data["id"]),
            "nome": data["nome"],
            "uf": _to_int(data["uf"]),
            "ibge": _to_int(data["ibge"]),
            "lat_lon": _to_point(data["lat_lon"]),
            "cod_tom": _to_int(data["cod_tom"]),
        })

    query = text("""
        INSERT INTO cidade (
            id,
            nome,
            uf,
            ibge,
            lat_lon,
            cod_tom
        )
        VALUES (
            :id,
            :nome,
            :uf,
            :ibge,
            :lat_lon,
            :cod_tom
        )
        ON CONFLICT (id)
        DO UPDATE SET
            nome = EXCLUDED.nome,
            uf = EXCLUDED.uf,
            ibge = EXCLUDED.ibge,
            lat_lon = EXCLUDED.lat_lon,
            cod_tom = EXCLUDED.cod_tom
    """)

    await session.execute(
        query,
        records
    )

async def _reset_sequences(session: AsyncSession) -> None:
    await session.execute(text("""
        SELECT setval(
            pg_get_serial_sequence('pais', 'id'),
            (SELECT MAX(id) FROM pais),
            true
        )
    """))

    await session.execute(text("""
        SELECT setval(
            pg_get_serial_sequence('estado', 'id'),
            (SELECT MAX(id) FROM estado),
            true
        )
    """))

    await session.execute(text("""
        SELECT setval(
            pg_get_serial_sequence('cidade', 'id'),
            (SELECT MAX(id) FROM cidade),
            true
        )
    """))

async def seed_geography(session: AsyncSession) -> None:
    print("Começando a seedar...")
    print("Seeding países...")
    await seed_paises(session)

    print("Seeding estados...")
    await seed_estados(session)

    print("Seeding cidades...")
    await seed_cidades(session)

    print("Atualizando sequences...")
    await _reset_sequences(session)

    print("Geografia populada com sucesso!")