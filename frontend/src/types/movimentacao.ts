import type { DecimalValue } from '@/types/produto'

export type TipoMovimentacao = 'ENTRADA' | 'SAIDA'
export type TipoSaida = 'VENDA' | 'PERDA' | 'AVARIA' | 'VENCIMENTO' | 'RECALL'

export type Entrada = Record<string, unknown> & {
    id: number
    data_entrada: string
    quantidade: DecimalValue
    preco_custo_unitario: DecimalValue
    tipo_entrada: string
    observacao: string | null

    fornecedor_id: number
    fornecedor_nome: string

    lote_id: number
    lote_numero: string

    produto_id: number
    produto_nome: string

    usuario_id: number
    usuario_nome: string

    estoque_id: number
    quantidade_atual: DecimalValue

    corredor: string
    prateleira: string
    secao: string
}

export interface EntradaListResponse {
    items: Entrada[]
    total: number
    page: number
    per_page: number
}

export type Saida = Record<string, unknown> & {
    id: number
    data_saida: string
    quantidade: DecimalValue
    tipo_saida: TipoSaida

    preco_venda_unitario: DecimalValue | null

    estoque_id: number

    lote_id: number
    lote_numero: string

    produto_id: number
    produto_nome: string

    usuario_id: number
    usuario_nome: string
}

export interface SaidaListResponse {
    items: Saida[]
    total: number
    page: number
    per_page: number
}

export interface EntradaCreatePayload {
    fornecedor_id: number
    lote_id: number
    quantidade: string
    preco_custo_unitario: string
    tipo_entrada: string
    observacao: string | null
    data_entrada?: string

    localizacao: {
        corredor: string
        prateleira: string
        secao: string
    }
}

export interface SaidaCreatePayload {
    estoque_id: number
    quantidade: string
    tipo_saida: TipoSaida
    preco_venda_unitario: string | null
    data_saida?: string
}