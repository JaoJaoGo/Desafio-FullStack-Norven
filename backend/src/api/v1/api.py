from fastapi import APIRouter

from api.v1.endpoints.usuarios import router as usuarios_router

api_router = APIRouter()

api_router.include_router(usuarios_router, prefix="/usuarios", tags=["usuarios"])