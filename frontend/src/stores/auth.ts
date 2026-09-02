import { defineStore } from 'pinia'
import { AUTH_TOKEN_KEY } from '@/services/api'
import { authService } from '@/services/authService'
import type { LoginCredentials } from '@/types/auth'

interface AuthState {
    token: string | null
}

export const useAuthStore = defineStore(
    'auth',
    {
        state: (): AuthState => ({
            token: localStorage.getItem(AUTH_TOKEN_KEY),
        }),

        getters: {
            isAuthenticated(state): boolean {
                return Boolean(state.token)
            },
        },

        actions: {
            async login(credentials: LoginCredentials): Promise<void> {
                const response = await authService.login(credentials)

                this.token = response.access_token

                localStorage.setItem(AUTH_TOKEN_KEY, response.access_token)
            },

            logout(): void {
                this.token = null

                localStorage.removeItem(AUTH_TOKEN_KEY)
            },
        },
    },
)