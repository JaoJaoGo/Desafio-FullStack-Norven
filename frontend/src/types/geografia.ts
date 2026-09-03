export interface Pais {
    id: number
    nome: string | null
    nome_pt: string | null
    sigla: string | null
    ddi: number | null
}

export interface Estado {
    id: number
    nome: string | null
    uf: string | null
    pais_id: number | null
}

export interface Cidade {
    id: number
    nome: string | null
    estado_id: number | null
}

export interface CidadeHierarquia {
    cidade: Cidade
    estado: Estado
    pais: Pais
}