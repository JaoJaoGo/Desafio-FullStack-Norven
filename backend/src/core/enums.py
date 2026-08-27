from enum import Enum

class NivelAcessoEnum(str, Enum):
    ADMINISTRADOR = "administrador"
    OPERADOR = "operador"

class TipoSaidaEnum(str, Enum):
    VENDA = "VENDA"
    PERDA = "PERDA"
    AVARIA = "AVARIA"
    VENCIMENTO = "VENCIMENTO"
    RECALL = "RECALL"