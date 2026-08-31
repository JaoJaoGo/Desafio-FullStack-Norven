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

class ProdutoStatusEnum(str, Enum):
    SEM_ESTOQUE = "SEM_ESTOQUE"
    VENCIDO = "VENCIDO"
    PROXIMO_VENCIMENTO = "PROXIMO_VENCIMENTO"
    ESTOQUE_BAIXO = "ESTOQUE_BAIXO"
    OK = "OK"

class TipoMovimentacaoEnum(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"