import { apiRequest } from '@/services/api'

import type { TransacaoListParams, TransacaoListResponse } from '@/types/transacao'

export const transacaoService = {
    async list(params: TransacaoListParams): Promise<TransacaoListResponse> {
        const query = new URLSearchParams()

        const search = params.search?.trim()
        const tipo = params.tipo?.trim()

        if (search) {
            query.set('search', search)
        }

        if (params.produtoId) {
            query.set('produto_id', String(params.produtoId))
        }

        if (params.movimento) {
            query.set('movimento', params.movimento)
        }

        if (tipo) {
            query.set(
                'tipo',
                tipo,
            )
        }

        if (params.usuarioId) {
            query.set(
                'usuario_id',
                String(params.usuarioId),
            )
        }

        if (params.quantidade) {
            query.set(
                'quantidade',
                params.quantidade,
            )
        }

        if (params.quantidadeMin) {
            query.set(
                'quantidade_min',
                params.quantidadeMin,
            )
        }

        if (params.quantidadeMax) {
            query.set(
                'quantidade_max',
                params.quantidadeMax,
            )
        }

        if (params.dataInicio) {
            query.set(
                'data_inicio',
                `${params.dataInicio}T00:00:00`,
            )
        }

        if (params.dataFim) {
            query.set(
                'data_fim',
                `${params.dataFim}T23:59:59`,
            )
        }

        query.set(
            'page',
            String(params.page),
        )

        query.set(
            'per_page',
            String(params.perPage),
        )

        return apiRequest<TransacaoListResponse>(
            `/transacoes/?${query.toString()}`,
            {
                method: 'GET',
            },
        )
    },
}