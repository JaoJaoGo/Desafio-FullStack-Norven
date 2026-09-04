export type Lote = Record<string, unknown> & {
    id: number
    numero: string
    data_validade: string | null
    produto_id: number
  }

export interface LoteListResponse {
  items: Lote[]
  total: number
  page: number
  per_page: number
}

export interface LoteCreatePayload {
  numero: string
  data_validade: string | null
  produto_id: number
}