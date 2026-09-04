export interface Categoria {
    id: number
    nome: string
}

export interface CategoriaListResponse {
    items: Categoria[]
    total: number
    page: number
    per_page: number
}

export interface CategoriaCreatePayload {
    nome: string
}