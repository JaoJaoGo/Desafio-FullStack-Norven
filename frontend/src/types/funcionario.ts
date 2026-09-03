export type NivelAcesso =
    | "administrador"
    | "operador"

export interface Contato {
    id: number
    cod_pais: string
    ddd: string
    numero: string
}

export interface Endereco {
    id: number
    logradouro: string
    numero: string
    complemento: string | null
    cep: string
    bairro: string
    municipio_id: number
}

export type Funcionario = Record<string, unknown> & {
    id: number
    nome: string
    email: string
    nivel_acesso: NivelAcesso
    endereco_id: number
    contato_id: number
}

export interface FuncionarioDetail extends Funcionario {
    endereco: Endereco
    contato: Contato
}

export interface FuncionarioListResponse {
    items: Funcionario[]
    total: number
    page: number
    per_page: number
}

export interface FuncionarioListParams {
    search?: string
    nivelAcesso?: NivelAcesso
    page: number
    perPage: number
}

export interface ContatoPayload {
    cod_pais: string
    ddd: string
    numero: string
}

export interface EnderecoPayload {
    logradouro: string
    numero: string
    complemento: string | null
    cep: string
    bairro: string
    municipio_id: number
}

export interface FuncionarioCreatePayload {
    nome: string
    email: string
    password: string
    nivel_acesso: NivelAcesso
    endereco: EnderecoPayload
    contato: ContatoPayload
}

export type FuncionarioUpdatePayload = Omit<FuncionarioCreatePayload, 'password'> & {
    password?: string
}