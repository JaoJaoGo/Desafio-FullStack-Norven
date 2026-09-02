from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models.__all_models
from api.v1.api import api_router
from core.configs import settings

app = FastAPI(title="Desafio FullStack Norven", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)