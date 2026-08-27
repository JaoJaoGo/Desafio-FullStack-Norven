from typing import Optional

from pydantic import BaseModel as SCBaseModel

class EstadoSchema(SCBaseModel):
    id: Optional[int] = None
    nome: str
    uf: str
    ibge: int
    pais_id: Optional[int] = None
    ddd: int

    class Config:
        from_attributes = True