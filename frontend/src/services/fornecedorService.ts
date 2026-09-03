import { apiRequest } from '@/services/api'

import type { FornecedorCreatePayload, FornecedorDetail, FornecedorListParams, FornecedorListResponse, FornecedorUpdatePayload } from '@/types/fornecedor'

export const fornecedorService = {
    async list(params: FornecedorListParams): Promise<FornecedorListResponse> {
        const query = new URLSearchParams()

        const search = params.search?.trim()

        if (search) {
            query.set('search', search)
        }

        query.set('page', String(params.page))
        query.set('per_page', String(params.perPage))

        return apiRequest<FornecedorListResponse>(`/fornecedores/?${query.toString()}`, {
            method: 'GET',
        })
    },

    async findById(fornecedorId: number): Promise<FornecedorDetail> {
        return apiRequest<FornecedorDetail>(`/fornecedores/${fornecedorId}`, {
            method: 'GET',
        })
    },

    async create(payload: FornecedorCreatePayload): Promise<FornecedorDetail> {
        return apiRequest<FornecedorDetail>('/fornecedores/', {
            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify(payload),
        })
    },

    async update(fornecedorId: number, payload: FornecedorUpdatePayload): Promise<FornecedorDetail> {
        return apiRequest<FornecedorDetail>(`/fornecedores/${fornecedorId}`, {
            method: 'PATCH',

            headers: {'Content-Type': 'application/json' },

            body: JSON.stringify(payload),
        })
    },
}
