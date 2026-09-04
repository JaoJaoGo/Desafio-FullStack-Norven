import type { Categoria } from '@/types/categoria'
import type { UnidadeMedida } from '@/types/unidadeMedida'

export type ProdutoStatus =
    | 'SEM_ESTOQUE'
    | 'VENCIDO'
    | 'PROXIMO_VENCIMENTO'
    | 'ESTOQUE_BAIXO'
    | 'OK'

export type DecimalValue = 
    | string
    | number

export type ProdutoListItem = Record<string, unknown> & {
    id: number
    cod_idt: string
    nome: string
    preco_venda_atual: DecimalValue
    eh_perecivel: boolean

    categoria_id: number
    categoria: string

    unidade_medida_id: number
    unidade_medida: string
    unidade_medida_sigla: string

    validade: string | null

    estoque_total: DecimalValue
    estoque_baixo: boolean

    status: ProdutoStatus
}

export interface ProdutoListResponse {
    items: ProdutoListItem[]
    total: number
    page: number
    per_page: number
}

export interface ProdutoListParams {
    nome?: string
    status?: ProdutoStatus
    precoMin?: string
    precoMax?: string
    page: number
    perPage: number
}

export interface ProdutoResponsavel {
    id: number
    nome: string
    email: string
}

export interface InformacaoNutricionalPayload {
    porcao_quantidade: string
    valor_energetico_kcal: string | null
    carboidratos_g: string | null
    proteinas_g: string | null
    gorduras_totais_g: string | null
    ingredientes: string | null
    alergenicos: string | null
    unidade_porcao_id: number    
}

export interface InformacaoNutricionalResponse {
    id: number
    porcao_quantidade: DecimalValue
    valor_energetico_kcal: DecimalValue | null
    carboidratos_g: DecimalValue | null
    proteinas_g: DecimalValue | null
    gorduras_totais_g: DecimalValue | null
    ingredientes: string | null
    alergenicos: string | null
    unidade_porcao_id: number
    unidade_porcao: UnidadeMedida
}

export interface ProdutoDetail {
    id: number
    cod_idt: string
    nome: string
    descricao: string | null
    preco_venda_atual: DecimalValue
    eh_perecivel: boolean
    data_cadastro: string

    usuario_id: number
    categoria_id: number
    unidade_medida_id: number
    informacao_nutricional_id: number | null

    responsavel: ProdutoResponsavel
    categoria: Categoria
    unidade_medida: UnidadeMedida
    informacao_nutricional: InformacaoNutricionalResponse | null

    validade: string | null
    estoque_total: DecimalValue
    estoque_baixo: boolean
    status: ProdutoStatus
}

export interface ProdutoCreatePayload {
    cod_idt: string
    nome: string
    descricao: string | null
    preco_venda_atual: string
    eh_perecivel: boolean
    categoria_id: number
    unidade_medida_id: number
    informacao_nutricional: InformacaoNutricionalPayload | null
}

export interface ProdutoUpdatePayload {
    cod_idt?: string
    nome?: string
    descricao?: string | null
    preco_venda_atual?: string
    eh_perecivel?: boolean
    categoria_id?: number
    unidade_medida_id?: number
    informacao_nutricional?: InformacaoNutricionalPayload | null
}