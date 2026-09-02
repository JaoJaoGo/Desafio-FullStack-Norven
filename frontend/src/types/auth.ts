export interface LoginCredentials {
    email: string
    password: string
}

export interface TokenResponse {
    access_token: string
    token_type: string
}