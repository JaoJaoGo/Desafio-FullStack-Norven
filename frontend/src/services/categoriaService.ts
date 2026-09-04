import { apiRequest } from '@/services/api'

import type { Categoria, CategoriaCreatePayload, CategoriaListResponse } from '@/types/categoria'

export const categoriaService = {
    async list(page = 1, perPage = 100): Promise<CategoriaListResponse> {
        const query = new URLSearchParams({
            page: String(page),
            per_page: String(perPage),
        })

        return apiRequest<CategoriaListResponse>(
            `/categorias/?${query.toString()}`,
            {
                method: 'GET',
            },
        )
    },

    async listAll(): Promise<Categoria[]> {
        const items: Categoria[] = []

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

    async create(payload: CategoriaCreatePayload): Promise<Categoria> {
        return apiRequest<Categoria>(
            '/categorias/',
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