from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.informacao_nutricional_model import InformacaoNutricionalModel
from models.usuario_model import UsuarioModel
from services.estoque_service import EstoqueService
from services.lote_service import LoteService
from repositories.categoria_repository import CategoriaRepository
from repositories.informacao_nutricional_repository import InformacaoNutricionalRepository
from repositories.lote_repository import LoteRepository
from repositories.produto_repository import ProdutoRepository
from repositories.unidade_medida_repository import UnidadeMedidaRepository
from schemas.informacao_nutricional_schema import InformacaoNutricionalCreateSchema
from schemas.produto_schema import ProdutoCreateSchema, ProdutoDetailResponseSchema, ProdutoFilterSchema, ProdutoListItemSchema, ProdutoUpdateSchema

class ProdutoService:
    # Validações auxiliares
    @staticmethod
    async def _validate_categoria(db: AsyncSession, categoria_id: int):
        categoria = await CategoriaRepository.find_by_id(db, categoria_id)

        if categoria is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        
        return categoria

    @staticmethod
    async def _validate_unidade(db: AsyncSession, unidade_id: int):
        unidade = await UnidadeMedidaRepository.find_by_id(db, unidade_id)

        if unidade is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidade de medida não encontrada"
            )
        
        return unidade

    @staticmethod
    async def _resolve_informacao_nutricional(db: AsyncSession, data: InformacaoNutricionalCreateSchema) -> InformacaoNutricionalModel:
        await ProdutoService._validate_unidade(db, data.unidade_porcao_id)

        informacao = await InformacaoNutricionalRepository.find_by_data(db, data)
        
        if informacao is not None:
            return informacao
        
        return await InformacaoNutricionalRepository.create(db, data)

    # CREATE
    @staticmethod
    async def create(db: AsyncSession, data: ProdutoCreateSchema, current_user: UsuarioModel) -> ProdutoDetailResponseSchema:
        try:
            # Nome único
            produto_nome = await ProdutoRepository.find_by_name(db, data.nome)

            if produto_nome is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um produto com este nome.")

            # Código único
            produto_codigo = await ProdutoRepository.find_by_code(db, data.cod_idt)

            if produto_codigo is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um produto com este código.")

            # Categoria
            await ProdutoService._validate_categoria(db, data.categoria_id)

            # Unidade de medida
            await ProdutoService._validate_unidade(db, data.unidade_medida_id)

            # Informação nutricional
            informacao_id: Optional[int] = None

            if data.informacao_nutricional is not None:
                informacao = await ProdutoService._resolve_informacao_nutricional(db, data.informacao_nutricional)

                informacao_id = informacao.id

            # Produto
            produto = (
                await ProdutoRepository.create(
                    db=db,
                    cod_idt=data.cod_idt,
                    nome=data.nome,
                    descricao=data.descricao,
                    preco_venda_atual=data.preco_venda_atual,
                    eh_perecivel=data.eh_perecivel,

                    # Responsável pelo cadastro vem do JWT
                    usuario_id=current_user.id,
                    categoria_id=data.categoria_id,
                    unidade_medida_id=data.unidade_medida_id,
                    informacao_nutricional_id=informacao_id
                )
            )

            # NÃO criamos lote aqui.
            # Produto perecível pode existir normalmente sem lote.

            await db.commit()

            return await ProdutoService.find_by_id(db, produto.id)
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()

            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível cadastrar o produto. Verifique os dados informados.")
        except Exception:
            await db.rollback()
            raise

    # LIST
    @staticmethod
    async def list(db: AsyncSession, filters: ProdutoFilterSchema):
        rows, total = await ProdutoRepository.list(db, filters)

        items = []

        for row in rows:
            produto = row[0]

            items.append(
                ProdutoListItemSchema(
                    id=produto.id,
                    cod_idt=produto.cod_idt,
                    nome=produto.nome,
                    preco_venda_atual=produto.preco_venda_atual,
                    eh_perecivel=produto.eh_perecivel,
                    categoria_id=produto.categoria_id,
                    categoria=row.categoria_nome,
                    unidade_medida_id=produto.unidade_medida_id,
                    unidade_medida=row.unidade_nome,
                    unidade_medida_sigla=row.unidade_sigla,
                    validade=row.validade,
                    estoque_total=row.estoque_total,
                    estoque_baixo=row.estoque_baixo,
                    status=row.status
                )
            )
        
        return items, total


    # FIND
    @staticmethod
    async def find_by_id(db: AsyncSession, produto_id: int) -> ProdutoDetailResponseSchema:
        produto = await ProdutoRepository.find_by_id(db, produto_id, with_relations=True)

        if produto is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado.")

        indicators = await ProdutoRepository.get_indicators(db, produto_id)
        lotes = await LoteService.list_by_product(db, produto_id)
        estoques = await EstoqueService.list_by_product(db, produto_id)

        return ProdutoDetailResponseSchema(
            id=produto.id,
            cod_idt=produto.cod_idt,
            nome=produto.nome,
            descricao=produto.descricao,
            preco_venda_atual=produto.preco_venda_atual,
            eh_perecivel=produto.eh_perecivel,
            data_cadastro=produto.data_cadastro,
            usuario_id=produto.usuario_id,
            categoria_id=produto.categoria_id,
            unidade_medida_id=produto.unidade_medida_id,
            informacao_nutricional_id=produto.informacao_nutricional_id,
            responsavel=produto.usuario,
            categoria=produto.categoria,
            unidade_medida=produto.unidade_medida,
            informacao_nutricional=produto.informacao_nutricional,
            validade=indicators.validade,
            estoque_total=indicators.estoque_total,
            estoque_baixo=indicators.estoque_baixo,
            status=indicators.status,
            lotes=lotes,
            estoques=estoques
        )

    # UPDATE
    @staticmethod
    async def update(db: AsyncSession, produto_id: int, data: ProdutoUpdateSchema) -> ProdutoDetailResponseSchema:
        produto = await ProdutoRepository.find_by_id(db, produto_id)

        if produto is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado.")

        try:
            values = {}

            # Código
            if data.cod_idt is not None and data.cod_idt != produto.cod_idt:
                encontrado = await ProdutoRepository.find_by_code(db, data.cod_idt)

                if encontrado is not None and encontrado.id != produto.id:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um produto com este código.")

                values["cod_idt"] = data.cod_idt

            # Nome
            if data.nome is not None and data.nome != produto.nome:
                encontrado = await ProdutoRepository.find_by_name(db, data.nome)

                if encontrado is not None and encontrado.id != produto.id:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um produto com este nome.")

                values["nome"] = data.nome

            # Descrição
            if "descricao" in data.model_fields_set:
                values["descricao"] = data.descricao

            # Preço
            if data.preco_venda_atual is not None:
                values["preco_venda_atual"] = data.preco_venda_atual

            # Perecibilidade
            if data.eh_perecivel is not None and data.eh_perecivel != produto.eh_perecivel:
                # Não perecível → perecível
                # NÃO exigimos que exista lote.
                # Apenas impedimos a alteração caso já existam lotes sem validade.
                if data.eh_perecivel:
                    possui_lote_sem_validade = await LoteRepository.exists_without_validity(db, produto.id)

                    if possui_lote_sem_validade:
                        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não é possível marcar o produto como perecível: existem lotes sem data de validade.")

                values["eh_perecivel"] = data.eh_perecivel

            # Categoria
            if data.categoria_id is not None:
                await ProdutoService._validate_categoria(db, data.categoria_id)

                values["categoria_id"] = data.categoria_id

            # Unidade de medida
            if data.unidade_medida_id is not None:
                await ProdutoService._validate_unidade(db, data.unidade_medida_id)

                values["unidade_medida_id"] = data.unidade_medida_id

            # Informação nutricional
            if "informacao_nutricional" in data.model_fields_set:

                if data.informacao_nutricional is None:
                    values["informacao_nutricional_id"] = None

                else:
                    informacao = await ProdutoService._resolve_informacao_nutricional(db, data.informacao_nutricional)

                    values["informacao_nutricional_id"] = informacao.id

            # Persistência
            if values:
                await ProdutoRepository.update(db, produto, values)

            await db.commit()

            return await ProdutoService.find_by_id(db, produto_id)
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()

            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar o produto. Verifique os dados informados.")
        except Exception:
            await db.rollback()
            raise