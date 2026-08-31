from datetime import datetime
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.produto_controller import ProdutoController
from controllers.entrada_controller import EntradaController
from controllers.saida_controller import SaidaController
from controllers.transacao_controller import TransacaoController
from core.deps import get_current_user, get_session
from core.enums import ProdutoStatusEnum, TipoMovimentacaoEnum
from models.usuario_model import UsuarioModel
from schemas.produto_schema import ProdutoCreateSchema, ProdutoDetailResponseSchema, ProdutoFilterSchema, ProdutoListResponseSchema, ProdutoUpdateSchema
from schemas.entrada_schema import EntradaResponseSchema, ProdutoEntradaCreateSchema
from schemas.saida_schema import ProdutoSaidaCreateSchema, SaidaResponseSchema
from schemas.transacao_schema import TransacaoFilterSchema, TransacaoListResponseSchema

router = APIRouter()

@router.post("/", response_model=ProdutoDetailResponseSchema, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_produto(data: ProdutoCreateSchema, db: AsyncSession = Depends(get_session), current_user: UsuarioModel = Depends(get_current_user)):
    return await ProdutoController.create(data, db, current_user)

@router.get("/", response_model=ProdutoListResponseSchema)
async def list_produtos(
    nome: Optional[str] = Query(default=None, description="Filtra pelo nome do produto"),
    categoria_id: Optional[int] = Query(default=None, ge=1),
    categoria: Optional[str] = Query(default=None, description="Filtra pelo nome da categoria"),
    status_produto: Optional[ProdutoStatusEnum] = Query(default=None, alias="status"),
    preco_min: Optional[Decimal] = Query(default=None, ge=0),
    preco_max: Optional[Decimal] = Query(default=None, ge=0),

    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),

    db: AsyncSession = Depends(get_session)
):
    filters = ProdutoFilterSchema(
        nome=nome,
        categoria_id=categoria_id,
        categoria=categoria,
        status=status_produto,
        preco_min=preco_min,
        preco_max=preco_max,
        page=page,
        per_page=per_page
    )

    items, total = await ProdutoController.list(db, filters)

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/{produto_id}", response_model=ProdutoDetailResponseSchema, dependencies=[Depends(get_current_user)])
async def get_produto(produto_id: int, db: AsyncSession = Depends(get_session)):
    return await ProdutoController.find_by_id(produto_id=produto_id, db=db)

@router.patch("/{produto_id}", response_model=ProdutoDetailResponseSchema, dependencies=[Depends(get_current_user)])
async def update_produto(produto_id: int, data: ProdutoUpdateSchema, db: AsyncSession = Depends(get_session)):
    return await ProdutoController.update(produto_id=produto_id, data=data, db=db)

@router.get('/{produto_id}/transacoes', response_model=TransacaoListResponseSchema, dependencies=[Depends(get_current_user)])
async def list_transacoes_produto(
    produto_id: int,
    search: Optional[str] = None,
    movimento: Optional[TipoMovimentacaoEnum] = None,
    tipo: Optional[str] = None,
    usuario_id: Optional[int] = Query(default=None, ge=1),
    quantidade: Optional[Decimal] = Query(default=None, gt=0),
    quantidade_min: Optional[Decimal] = Query(default=None, ge=0),
    quantidade_max: Optional[Decimal] = Query(default=None, ge=0),
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    filters = TransacaoFilterSchema(
        search=search,
        movimento=movimento,
        tipo=tipo,
        usuario_id=usuario_id,
        quantidade=quantidade,
        quantidade_min=quantidade_min,
        quantidade_max=quantidade_max,
        data_inicio=data_inicio,
        data_fim=data_fim,
        page=page,
        per_page=per_page
    )

    items, total = await TransacaoController.list_by_product(db, produto_id, filters)

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.post('/{produto_id}/transacoes/entrada', response_model=EntradaResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_entrada_produto(produto_id: int, data: ProdutoEntradaCreateSchema, db: AsyncSession = Depends(get_session), current_user: UsuarioModel = Depends(get_current_user)):
    return await EntradaController.create(db, produto_id, data, current_user)

@router.post('/{produto_id}/transacoes/saida', response_model=SaidaResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_saida_produto(produto_id: int, data: ProdutoSaidaCreateSchema, db: AsyncSession = Depends(get_session), current_user: UsuarioModel = Depends(get_current_user)):
    return await SaidaController.create(db, produto_id, data, current_user)