import { apiRequest } from '@/services/api'

import type { ProdutoCreatePayload, ProdutoDetail, ProdutoListParams, ProdutoListResponse, ProdutoUpdatePayload } from '@/types/produto'

export const produtoService = {
    async list(params: ProdutoListParams): Promise<ProdutoListResponse> {
        const query = new URLSearchParams()

        const nome = params.nome?.trim()

        if (nome) {
            query.set('nome', nome)
        }

        if (params.status) {
            query.set('status', params.status)
        }

        if (params.precoMin) {
            query.set('preco_min', params.precoMin)
        }

        if (params.precoMax) {
            query.set('preco_max', params.precoMax)
        }

        query.set('page', String(params.page))
        query.set('per_page', String(params.perPage))

        return apiRequest<ProdutoListResponse>(
            `/produtos/?${query.toString()}`,
            {
                method: 'GET',
            },
        )
    },

    async findById(produtoId: number): Promise<ProdutoDetail> {
        return apiRequest<ProdutoDetail>(
            `/produtos/${produtoId}`,
            {
                method: 'GET',
            },
        )
    },

    async create(payload: ProdutoCreatePayload): Promise<ProdutoDetail> {
        return apiRequest<ProdutoDetail>(
            '/produtos/',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            },
        )
    },

    async update(produtoId: number, payload: ProdutoUpdatePayload): Promise<ProdutoDetail> {
        return apiRequest<ProdutoDetail>(
            `/produtos/${produtoId}`,
            {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            },
        )
    },
}