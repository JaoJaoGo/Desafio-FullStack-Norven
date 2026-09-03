export interface ContatoFornecedor {
    id: number
    cod_pais: string
    ddd: string
    numero: string
}

export interface EnderecoFornecedor {
    id: number
    logradouro: string
    numero: string
    complemento: string | null
    cep: string
    bairro: string
    municipio_id: number
}

export type Fornecedor = Record<string, unknown> & {
    id: number
    nome: string
    cnpj: string
}

export interface FornecedorDetail extends Fornecedor {
    endereco_id: number
    contato_id: number
    endereco: EnderecoFornecedor
    contato: ContatoFornecedor
}

export interface FornecedorListResponse {
    items: Fornecedor[]
    total: number
    page: number
    per_page: number
}

export interface FornecedorListParams {
    search?: string
    page: number
    perPage: number
}

export interface FornecedorContatoPayload {
    cod_pais: string
    ddd: string
    numero: string
}

export interface FornecedorEnderecoPayload {
    logradouro: string
    numero: string
    complemento: string | null
    cep: string
    bairro: string
    municipio_id: number
}

export interface FornecedorCreatePayload {
    nome: string
    cnpj: string
    endereco: FornecedorEnderecoPayload
    contato: FornecedorContatoPayload
}

export type FornecedorUpdatePayload = Partial<FornecedorCreatePayload>