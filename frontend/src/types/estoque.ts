import type { DecimalValue } from "./produto"

export type Estoque = Record<string, unknown> & {
    id: number
    quantidade_atual: DecimalValue
    corredor: string
    prateleira: string
    secao: string

    entrada_id: number

    lote_id: number
    lote_numero: string

    produto_id: number
    produto_nome: string
}

export interface EstoqueListResponse {
    items: Estoque[]
    total: number
    page: number
    per_page: number
}