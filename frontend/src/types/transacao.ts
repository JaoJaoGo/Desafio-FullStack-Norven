import type { DecimalValue } from '@/types/produto'

export type TipoMovimentacao =
    | 'ENTRADA'
    | "SAIDA"

export type Transacao = Record<string, unknown> & {
    id: number

    movimento: TipoMovimentacao
    data: string

    quantidade: DecimalValue
    tipo: string

    produto_id: number
    produto_nome: string

    usuario_id: number
    usuario_nome: string

    lote_id: number
    lote_numero: string

    estoque_id: number | null
    
    fornecedor_id: number | null
    fornecedor_nome: string | null

    preco_unitario: DecimalValue | null
    observacao: string | null
}

export interface TransacaoListResponse {
    items: Transacao[]
    total: number
    page: number
    per_page: number
}

export interface TransacaoListParams {
    search?: string

    produtoId?: number
    movimento?: TipoMovimentacao
    tipo?: string
    usuarioId?: number

    quantidade?: string
    quantidadeMin?: string
    quantidadeMax?: string

    dataInicio?: string
    dataFim?: string

    page: number
    perPage: number
}