const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

interface FastApiErrorResponse {
    detail?: unknown
}

interface ApiAuthHandlers {
    getAccessToken: () => string | null
    onUnauthorized: () => void
}

let getAccessToken: ApiAuthHandlers['getAccessToken'] = () => null
let onUnauthorized: ApiAuthHandlers['onUnauthorized'] = () => {}

export class ApiError extends Error {
    status: number

    constructor(status: number, message: string) {
        super(message)

        this.name = 'ApiError'
        this.status = status
    }
}

export function configureApiAuth(handlers: ApiAuthHandlers): void {
    getAccessToken = handlers.getAccessToken
    onUnauthorized = handlers.onUnauthorized
}

function getErrorMessage(payload: FastApiErrorResponse | null, fallback: string): string {
    if (typeof payload?.detail == 'string') {
        return payload.detail
    }

    return fallback
}

export async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers)

    const token = getAccessToken()

    if (token) {
        headers.set('Authorization', `Bearer ${token}`)
    }

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers,
        },
    )

    if (!response.ok) {
        let payload: FastApiErrorResponse | null = null

        try {
            payload = await response.json()
        } catch {
            payload = null
        }

        if (response.status === 401) {
            onUnauthorized()
        }

        throw new ApiError(response.status, getErrorMessage(payload, 'Ocorreu um erro ao comunicar com a API.'))
    }

    if (response.status === 204) {
        return undefined as T
    }

    return response.json() as Promise<T>
}