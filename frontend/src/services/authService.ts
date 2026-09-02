import { apiRequest } from '@/services/api'
import type { LoginCredentials, TokenResponse } from '@/types/auth'

export const authService = {
    async login(credentials: LoginCredentials): Promise<TokenResponse> {
        const body = new URLSearchParams()

        body.set('username', credentials.email)
        body.set('password', credentials.password)

        return apiRequest<TokenResponse>(
            '/auth/login',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body,
            },
        )
    },
}