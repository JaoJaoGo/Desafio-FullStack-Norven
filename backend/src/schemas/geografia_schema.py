from typing import Optional
from pydantic import BaseModel as SCBaseModel
from pydantic_settings import SettingsConfigDict

class PaisResponseSchema(SCBaseModel):
    id: int
    nome: Optional[str]
    nome_pt: Optional[str]
    sigla: Optional[str]
    ddi: Optional[int]

    model_config = SettingsConfigDict(
        from_attributes=True
    )

class EstadoResponseSchema(SCBaseModel):
    id: int
    nome: Optional[str]
    uf: Optional[str]
    pais_id: Optional[int]

    model_config = SettingsConfigDict(
        from_attributes=True
    )

class CidadeResponseSchema(SCBaseModel):
    id: int
    nome: Optional[str]
    estado_id: Optional[int]

    model_config = SettingsConfigDict(
        from_attributes=True
    )

class CidadeHierarquiaResponseSchema(SCBaseModel):
    cidade: CidadeResponseSchema
    estado: EstadoResponseSchema
    pais: PaisResponseSchema