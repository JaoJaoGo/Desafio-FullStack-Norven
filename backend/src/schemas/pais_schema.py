from typing import Optional

from pydantic import BaseModel as SCBaseModel

class PaisSchema(SCBaseModel):
    id: Optional[int] = None
    nome: str
    nome_pt: str
    sigla: str
    bacen: int
    ddi: int
    
    class Config:
        from_attributes = True