from datetime import date, datetime
from typing import Optional

def build_endereco_payload(municipio_id: int, indice: int = 1) -> dict:
    return {
        "logradouro": f"Rua de Teste {indice}",
        "numero": str(indice),
        "complemento": f"Sala {indice}",
        "cep": f"74000-{indice:03d}",
        "bairro": f"Bairro Teste {indice}",
        "municipio_id": municipio_id,
    }

def build_contato_payload(indice: int = 1) -> dict:
    return {
        "cod_pais": "+55",
        "ddd": "62",
        "numero": f"9{indice:08d}"
    }

def build_usuario_payload(municipio_id: int, indice: int = 1) -> dict:
    return {
        "nome": f"Usuário Teste {indice}",
        "email": f"usuario.teste.{indice}@norven.com.br",
        "password": "SenhaTeste123",
        "nivel_acesso": "operador",
        "endereco": build_endereco_payload(municipio_id, indice),
        "contato": build_contato_payload(indice)
    }

def build_fornecedor_payload(municipio_id: int, indice: int = 1) -> dict:
    return {
        "nome": f"Fornecedor Teste {indice}",
        "cnpj": f"{indice:014d}",
        "endereco": build_endereco_payload(municipio_id, indice + 100),
        "contato": build_contato_payload(indice + 100),
    }


def build_informacao_nutricional_payload(unidade_porcao_id: int) -> dict:
    return {
        "porcao_quantidade": "100.00",
        "valor_energetico_kcal": "250.00",
        "carboidratos_g": "35.00",
        "proteinas_g": "10.00",
        "gorduras_totais_g": "8.00",
        "ingredientes": "Aveia, açúcar e cacau.",
        "alergenicos": "Contém derivados de aveia.",
        "unidade_porcao_id": unidade_porcao_id
    }

def build_produto_payload(categoria_id: int, unidade_medida_id: int, indice: int = 1, eh_perecivel: bool = False, informacao_nutricional: Optional[dict] = None) -> dict:
    payload = {
        "cod_idt": f"PROD-TESTE-{indice:03d}",
        "nome": f"Produto Teste {indice}",
        "descricao": f"Descrição do produto de teste {indice}",
        "preco_venda_atual": "12.50",
        "eh_perecivel": eh_perecivel,
        "categoria_id": categoria_id,
        "unidade_medida_id": unidade_medida_id
    }

    if informacao_nutricional is not None:
        payload["informacao_nutricional"] = informacao_nutricional
    
    return payload

def build_lote_payload(produto_id: int, indice: int = 1, data_validade: Optional[date | str] = None) -> dict:
    if isinstance(data_validade, date):
        data_validade = data_validade.isoformat()
    
    return {
        "numero": f"LOTE-TESTE-{indice:03d}",
        "produto_id": produto_id,
        "data_validade": data_validade
    }

def build_entrada_payload(
    produto_id: int,
    fornecedor_id: int,
    lote_id: Optional[int] = None,
    indice: int = 1,
    quantidade: str = "10.000",
    preco_custo_unitario: str = "5.50",
    tipo_entrada: str = "COMPRA",
    observacao: Optional[str] = None,
    data_entrada: Optional[datetime | str] = None,
    novo_lote: Optional[dict] = None
) -> dict:
    payload = {
        "produto_id": produto_id,
        "fornecedor_id": fornecedor_id,
        "quantidade": quantidade,
        "preco_custo_unitario": preco_custo_unitario,
        "tipo_entrada": tipo_entrada,
        "observacao": observacao if observacao is not None else f"Entrada de teste {indice}",
        "localizacao": {
            "corredor": f"C{indice}",
            "prateleira": f"P{indice}",
            "secao": f"S{indice}",
        },
    }

    if lote_id is not None:
        payload["lote_id"] = lote_id

    if novo_lote is not None:
        payload["novo_lote"] = novo_lote

    if isinstance(data_entrada, datetime):
        data_entrada = data_entrada.isoformat()
    
    if data_entrada is not None:
        payload["data_entrada"] = data_entrada
    
    return payload

def build_saida_payload(
    produto_id: int,
    estoque_id: int,
    quantidade: str = "2.000",
    tipo_saida: str = "VENDA",
    preco_venda_unitario: Optional[str] = None,
    data_saida: Optional[datetime | str] = None,
) -> dict:
    payload = {
        "produto_id": produto_id,
        "estoque_id": estoque_id,
        "quantidade": quantidade,
        "tipo_saida": tipo_saida,
    }

    if preco_venda_unitario is not None:
        payload["preco_venda_unitario"] = preco_venda_unitario

    if isinstance(data_saida, datetime):
        data_saida = data_saida.isoformat()

    if data_saida is not None:
        payload["data_saida"] = data_saida

    return payload