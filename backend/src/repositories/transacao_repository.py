from sqlalchemy import cast, func, Integer, literal, Numeric, select, String, Text, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from models.entrada_model import EntradaModel
from models.estoque_model import EstoqueModel
from models.fornecedor_model import FornecedorModel
from models.lote_model import LoteModel
from models.saida_model import SaidaModel
from models.usuario_model import UsuarioModel
from schemas.transacao_schema import TransacaoFilterSchema

class TransacaoRepository:
    @staticmethod
    async def list_by_product(db: AsyncSession, produto_id: int, filters: TransacaoFilterSchema):
        entrada_query = (
            select(
                EntradaModel.id.label("id"),
                literal("ENTRADA").label("movimento"),
                EntradaModel.data_entrada.label("data"),
                EntradaModel.quantidade.label("quantidade"),
                EntradaModel.tipo_entrada.label("tipo"),
                EntradaModel.usuario_id.label("usuario_id"),
                UsuarioModel.nome.label("usuario_nome"),
                LoteModel.id.label("lote_id"),
                LoteModel.numero.label("lote_numero"),
                EstoqueModel.id.label("estoque_id"),
                FornecedorModel.id.label("fornecedor_id"),
                FornecedorModel.nome.label("fornecedor_nome"),
                EntradaModel.preco_custo_unitario.label("preco_unitario"),
                EntradaModel.observacao.label("observacao")
            )
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(UsuarioModel, UsuarioModel.id == EntradaModel.usuario_id)
            .join(FornecedorModel, FornecedorModel.id == EntradaModel.fornecedor_id)
            .outerjoin(EstoqueModel, EstoqueModel.entrada_id == EntradaModel.id)
            .where(LoteModel.produto_id == produto_id)
        )

        saida_query = (
            select(
                SaidaModel.id.label("id"),
                literal("SAIDA").label("movimento"),
                SaidaModel.data_saida.label("data"),
                SaidaModel.quantidade.label("quantidade"),
                cast(SaidaModel.tipo_saida, String(30)).label("tipo"),
                SaidaModel.usuario_id.label("usuario_id"),
                UsuarioModel.nome.label("usuario_nome"),
                LoteModel.id.label("lote_id"),
                LoteModel.numero.label("lote_numero"),
                EstoqueModel.id.label("estoque_id"),
                cast(literal(None), Integer).label("fornecedor_id"),
                cast(literal(None), String(50)).label("fornecedor_nome"),
                cast(SaidaModel.preco_venda_unitario, Numeric(10, 2)).label("preco_unitario"),
                cast(literal(None), Text).label("observacao")
            )
            .join(EstoqueModel, EstoqueModel.id == SaidaModel.estoque_id)
            .join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
            .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
            .join(UsuarioModel, UsuarioModel.id == SaidaModel.usuario_id)
            .where(LoteModel.produto_id == produto_id)
        )

        combined = union_all(entrada_query, saida_query).subquery("transacoes")

        conditions = []

        if filters.search:
            value = f"%{filters.search.strip()}%"

            conditions.append(
                (combined.c.usuario_nome.ilike(value)) |
                (combined.c.lote_numero.ilike(value))  |
                (combined.c.tipo.ilike(value))         |
                (combined.c.fornecedor_nome.ilike(value))
            )

        if filters.movimento is not None:
            conditions.append(combined.c.movimento == filters.movimento.value)

        if filters.tipo:
            conditions.append(func.upper(combined.c.tipo) == filters.tipo.strip().upper())

        if filters.usuario_id is not None:
            conditions.append(combined.c.usuario_id == filters.usuario_id)

        if filters.quantidade is not None:
            conditions.append(combined.c.quantidade == filters.quantidade)

        if filters.quantidade_min is not None:
            conditions.append(combined.c.quantidade >= filters.quantidade_min)

        if filters.quantidade_max is not None:
            conditions.append(combined.c.quantidade <= filters.quantidade_max)

        if filters.data_inicio is not None:
            conditions.append(combined.c.data >= filters.data_inicio)

        if filters.data_fim is not None:
            conditions.append(combined.c.data <= filters.data_fim)

        filtered_query = select(combined)

        if conditions:
            filtered_query = filtered_query.where(*conditions)

        count_query = select(func.count()).select_from(filtered_query.subquery())

        total = (await db.execute(count_query)).scalar_one()

        query = (
            filtered_query
            .order_by(combined.c.data.desc(), combined.c.id.desc())
            .offset((filters.page - 1) * filters.per_page)
            .limit(filters.per_page)
        )

        result = await db.execute(query)

        return result.mappings().all(), total