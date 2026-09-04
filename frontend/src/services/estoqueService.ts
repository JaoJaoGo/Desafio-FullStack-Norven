import { apiRequest } from '@/services/api'

import type { Estoque, EstoqueListResponse } from '@/types/estoque'

export const estoqueService = {
    async listByProduct(produtoId: number, somenteComSaldo = false, page = 1, perPage = 100): Promise<EstoqueListResponse> {
        const query = new URLSearchParams({
            produto_id: String(produtoId),
            somente_com_saldo: String(somenteComSaldo),
            page: String(page),
            per_page: String(perPage),
        })

        return apiRequest<EstoqueListResponse>(
            `/estoques/?${query.toString()}`,
            {
                method: 'GET',
            },
        )
    },

    async listAllByProduct(produtoId: number, somenteComSaldo = false): Promise<Estoque[]> {
        const items: Estoque[] = []

        let page = 1

        while (true) {
            const response = await this.listByProduct(produtoId, somenteComSaldo, page, 100)

            items.push(
                ...response.items,
            )

            if (items.length >= response.total || response.items.length === 0) {
                break
            }

            page += 1
        }
        
        return items
    },
}