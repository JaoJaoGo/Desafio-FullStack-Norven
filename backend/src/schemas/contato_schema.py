from typing import Optional
from pydantic import BaseModel as SCBaseModel

class ContatoBaseSchema(SCBaseModel):
    cod_pais: str
    ddd: str
    numero: str

class ContatoCreateSchema(ContatoBaseSchema):
    pass

class ContatoUpdateSchema(SCBaseModel):
    cod_pais: Optional[str] = None
    ddd: Optional[str] = None
    numero: Optional[str] = None

class ContatoResponseSchema(ContatoBaseSchema):
    id: int

    class Config:
        from_attributes = True