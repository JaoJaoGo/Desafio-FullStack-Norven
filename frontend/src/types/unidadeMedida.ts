export interface UnidadeMedida {
    id: number
    nome: string
    sigla: string
}

export interface UnidadeMedidaListResponse {
    items: UnidadeMedida[]
    total: number
    page: number
    per_page: number
}

export interface UnidadeMedidaCreatePayload {
    nome: string
    sigla: string
}