import { apiRequest } from '@/services/api'

import type { Entrada, EntradaCreatePayload, EntradaListResponse, Saida, SaidaCreatePayload, SaidaListResponse } from '@/types/movimentacao'

export const movimentacaoService = {
    async listEntradas(produtoId: number, page: number, perPage: number): Promise<EntradaListResponse> {
        const query = new URLSearchParams({
            produto_id: String(produtoId),
            page: String(page),
            per_page: String(perPage),
        })

        return apiRequest<EntradaListResponse>(
            `/entradas/?${query.toString()}`,
            {
                method: 'GET',
            },
        )
    },

    async listSaidas(produtoId: number, page: number, perPage: number): Promise<SaidaListResponse> {
        const query = new URLSearchParams({
            produto_id: String(produtoId),
            page: String(page),
            per_page: String(perPage),
        })

        return apiRequest<SaidaListResponse>(
            `/saidas/?${query.toString()}`,
            {
                method: 'GET',
            },
        )
    },

    async createEntrada(produtoId: number, payload: EntradaCreatePayload): Promise<Entrada> {
        return apiRequest<Entrada>(
            `/produtos/${produtoId}/transacoes/entrada`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            },
        )
    },

    async createSaida(produtoId: number, payload: SaidaCreatePayload): Promise<Saida> {
        return apiRequest<Saida>(
            `/produtos/${produtoId}/transacoes/saida`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            },
        )
    },

    async listEntradasByFornecedor(fornecedorId: number, page: number, perPage: number): Promise<EntradaListResponse> {
        const query = new URLSearchParams({
            fornecedor_id: String(fornecedorId),
            page: String(page),
            per_page: String(perPage),
        })

        return apiRequest<EntradaListResponse>(
            `/entradas/?${query.toString()}`,
            {
                method: 'GET',
            },
        )
    },

    async listSaidasByFuncionario(funcionarioId: number, page: number, perPage: number): Promise<SaidaListResponse> {
        const query = new URLSearchParams({
            usuario_id: String(funcionarioId),
            page: String(page),
            per_page: String(perPage),
        })

        return apiRequest<SaidaListResponse>(
            `/saidas/?${query.toString()}`,
            {
                method: 'GET',
            },
        )
    },

    async getEntradaTotal(): Promise<number> {
        const query = new URLSearchParams({
            page: '1',
            per_page: '1',
        })

        const response = await apiRequest<EntradaListResponse>(
            `/entradas/?${query.toString()}`,
            {
                method: 'GET',
            },
        )

        return response.total
    },

    async getSaidaTotal(): Promise<number> {
        const query = new URLSearchParams({
            page: '1',
            per_page: '1',
        })

        const response = await apiRequest<SaidaListResponse>(
            `/saidas/?${query.toString()}`,
            {
                method: 'GET',
            },
        )

        return response.total
    },
}