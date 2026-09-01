from fastapi import FastAPI

import models.__all_models
from api.v1.api import api_router
from core.configs import settings

app = FastAPI(title="Desafio FullStack Norven", version="1.0.0")

app.include_router(api_router, prefix=settings.API_V1_STR)