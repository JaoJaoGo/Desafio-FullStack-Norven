import { apiRequest } from '@/services/api'

import type { UnidadeMedida, UnidadeMedidaCreatePayload, UnidadeMedidaListResponse } from '@/types/unidadeMedida'

export const unidadeMedidaService = {
    async list(page = 1, perPage = 100): Promise<UnidadeMedidaListResponse> {
        const query = new URLSearchParams({
            page: String(page),
            per_page: String(perPage),
        })

        return apiRequest<UnidadeMedidaListResponse>(
            `/unidades-medidas/?${query.toString()}`,
            {
                method: 'GET',
            },
        )
    },

    async listAll(): Promise<UnidadeMedida[]> {
        const items: UnidadeMedida[] = []

        let page = 1

        while (true) {
            const response = await this.list(page, 100)

            items.push(...response.items)

            if (items.length >= response.total || response.items.length === 0) {
                break
            }

            page += 1
        }

        return items
    },

    async create(payload: UnidadeMedidaCreatePayload): Promise<UnidadeMedida> {
        return apiRequest<UnidadeMedida>(
            '/unidades-medidas/',
            {
                method: 'POST',

                headers: {
                    'Content-Type': 'application/json',
                },

                body: JSON.stringify(payload),
            },
        )
    },
}