from fastapi import APIRouter

from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.usuarios import router as usuarios_router
from api.v1.endpoints.produtos import router as produtos_router
from api.v1.endpoints.categorias import router as categorias_router
from api.v1.endpoints.unidades_medidas import router as unidades_medidas_router
from api.v1.endpoints.fornecedores import router as fornecedores_router
from api.v1.endpoints.geografia import router as geografia_router
from api.v1.endpoints.lotes import router as lotes_router
from api.v1.endpoints.entradas import router as entradas_router
from api.v1.endpoints.estoques import router as estoques_router
from api.v1.endpoints.saidas import router as saidas_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(usuarios_router, prefix="/usuarios", tags=["Usuários"])
api_router.include_router(geografia_router, prefix="/geografia", tags=["Geografia"])
api_router.include_router(produtos_router, prefix="/produtos", tags=["Produtos"])
api_router.include_router(categorias_router, prefix="/categorias", tags=["Categorias"])
api_router.include_router(unidades_medidas_router, prefix="/unidades-medidas", tags=["Unidades de Medida"])
api_router.include_router(fornecedores_router, prefix="/fornecedores", tags=["Fornecedores"])
api_router.include_router(lotes_router, prefix="/lotes", tags=["Lotes"])
api_router.include_router(entradas_router, prefix="/entradas", tags=["Entradas"])
api_router.include_router(estoques_router, prefix="/estoques", tags=["Estoques"])
api_router.include_router(saidas_router, prefix="/saidas", tags=["Saídas"])