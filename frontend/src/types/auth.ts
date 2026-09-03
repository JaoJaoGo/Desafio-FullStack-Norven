import type { NivelAcesso } from "@/types/funcionario"

export interface LoginCredentials {
    email: string
    password: string
}

export interface TokenResponse {
    access_token: string
    token_type: string
}

export interface AuthenticatedUser {
    id: number
    nome: string
    email: string
    nivel_acesso: NivelAcesso
    endereco_id: number
    contato_id: number
}