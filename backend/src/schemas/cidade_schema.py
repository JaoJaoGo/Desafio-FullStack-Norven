from typing import Optional, Any

from pydantic import field_validator, BaseModel as SCBaseModel

class CoordenadaSchema(SCBaseModel):
    latitude: float
    longitude: float

class CidadeSchema(SCBaseModel):
    id: Optional[int] = None
    nome: str
    estado_id: Optional[int] = None
    ibge: int
    lat_lon: Optional[CoordenadaSchema] = None
    cod_tom: int

    class Config:
        from_attributes = True

    @field_validator("lat_lon", mode="before")
    @classmethod
    def converter_point(cls, value: Any):
        if value is None:
            return None

        if hasattr(value, 'x') and hasattr(value, 'y'):
            return {
                "latitude": float(value.x),
                "longitude": float(value.y)
            }

        if isinstance(value, (tuple, list)) and len(value) == 2:
            return {
                "latitude": float(value[0]),
                "longitude": float(value[1])
            }
        
        if isinstance(value, str):
            value = value.strip("()")
            latitude, longitude = value.split(",")

            return {
                "latitude": float(latitude),
                "longitude": float(longitude)
            }

        return value