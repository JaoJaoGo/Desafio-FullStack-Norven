from datetime import datetime
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.transacao_controller import TransacaoController
from core.deps import get_current_user, get_session
from core.enums import TipoMovimentacaoEnum
from schemas.transacao_schema import TransacaoFilterSchema, TransacaoListResponseSchema

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.get('/', response_model=TransacaoListResponseSchema)
async def list_transacoes(
    search: Optional[str] = None,
    
    produto_id: Optional[int] = Query(default=None, ge=1),
    
    movimento: Optional[TipoMovimentacaoEnum] = None,
    tipo: Optional[str] = None,
    
    usuario_id: Optional[int] = Query(default=None, ge=1),
    
    quantidade: Optional[Decimal] = Query(default=None, ge=0),
    quantidade_min: Optional[Decimal] = Query(default=None, ge=0),
    quantidade_max: Optional[Decimal] = Query(default=None, ge=0),
    
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=1, ge=1, le=100),
    
    db: AsyncSession = Depends(get_session),
):
    filters = TransacaoFilterSchema(
        search=search,
        produto_id=produto_id,
        movimento=movimento,
        tipo=tipo,
        usuario_id=usuario_id,
        quantidade=quantidade,
        quantidade_min=quantidade_min,
        quantidade_max=quantidade_max,
        data_inicio=data_inicio,
        data_fim=data_fim,
        page=page,
        per_page=per_page,
    )
    
    items, total = await TransacaoController.list(db, filters)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
    }