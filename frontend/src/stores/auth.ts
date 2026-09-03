import { defineStore } from 'pinia'
import { AUTH_TOKEN_KEY } from '@/services/api'
import { authService } from '@/services/authService'
import type { LoginCredentials, AuthenticatedUser } from '@/types/auth'

interface AuthState {
    token: string | null
    user: AuthenticatedUser | null
}

export const useAuthStore = defineStore(
    'auth',
    {
        state: (): AuthState => ({
            token: localStorage.getItem(AUTH_TOKEN_KEY),

            user: null,
        }),

        getters: {
            isAuthenticated(state): boolean {
                return Boolean(state.token)
            },

            currentUserId(state): number | null {
                return state.user?.id ?? null
            },
        },

        actions: {
            async login(credentials: LoginCredentials): Promise<void> {
                const response = await authService.login(credentials)

                this.token = response.access_token

                localStorage.setItem(AUTH_TOKEN_KEY, response.access_token)

                try {
                    await this.fetchCurrentUser()
                } catch (error) {
                    this.logout()
                    throw error
                }
            },

            async fetchCurrentUser(): Promise<void> {
                if (!this.token) {
                    this.user = null
                    return
                }

                this.user = await authService.me()
            },

            async ensureCurrentUser(): Promise<void> {
                if (this.token && !this.user) {
                    await this.fetchCurrentUser()
                }
            },

            logout(): void {
                this.token = null
                this.user = null

                localStorage.removeItem(AUTH_TOKEN_KEY)
            },
        },
    },
)