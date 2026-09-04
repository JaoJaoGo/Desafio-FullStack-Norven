import { apiRequest } from '@/services/api'

import type { Lote, LoteCreatePayload, LoteListResponse } from '@/types/lote'

export const loteService = {
    async listByProduct(produtoId: number, page: number, perPage: number): Promise<LoteListResponse> {
        const query = new URLSearchParams({
            produto_id: String(produtoId),
            page: String(page),
            per_page: String(perPage),
        })

        return apiRequest<LoteListResponse>(
            `/lotes/?${query.toString()}`,
            {
                method: 'GET',
            },
        )
    },

    async listAllByProduct(produtoId: number): Promise<Lote[]> {
        const items: Lote[] = []

        let page = 1

        while (true) {
            const response = await this.listByProduct(produtoId, page, 100)

            items.push(...response.items)

            if (items.length >= response.total || response.items.length === 0) {
                break
            }

            page += 1
        }

        return items
    },

    async create(payload: LoteCreatePayload): Promise<Lote> {
        return apiRequest<Lote>(
            '/lotes/',
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