import { apiRequest } from "@/services/api"

import type { Cidade, CidadeHierarquia, Estado, Pais } from '@/types/geografia'

export const geografiaService = {
    async listPaises(): Promise<Pais[]> {
        return apiRequest<Pais[]>('/geografia/paises', {
            method: 'GET'
        })
    },

    async listEstados(paisId: number): Promise<Estado[]> {
        const query = new URLSearchParams({
            pais_id: String(paisId)
        })

        return apiRequest<Estado[]>(`/geografia/estados?${query.toString()}`, {
            method: 'GET'
        })
    },

    async listCidades(estadoId: number): Promise<Cidade[]> {
        const query = new URLSearchParams({
            estado_id: String(estadoId)
        })

        return apiRequest<Cidade[]>(`/geografia/cidades?${query.toString()}`, {
            method: 'GET'
        })
    },

    async findCidadeHierarquia(cidadeId: number): Promise<CidadeHierarquia> {
        return apiRequest<CidadeHierarquia>(`/geografia/cidades/${cidadeId}/hierarquia`, {
            method: 'GET'
        })
    }
}