from enum import Enum

class NivelAcessoEnum(str, Enum):
    ADMINISTRADOR = "administrador"
    OPERADOR = "operador"