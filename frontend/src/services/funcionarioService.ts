import { apiRequest } from '@/services/api'
import type { Funcionario, FuncionarioCreatePayload, FuncionarioDetail, FuncionarioListParams, FuncionarioListResponse, FuncionarioUpdatePayload } from '@/types/funcionario'

export const funcionarioService = {
  async list(params: FuncionarioListParams): Promise<FuncionarioListResponse> {
    const query = new URLSearchParams()

    const search = params.search?.trim()

    const nivelAcesso = params.nivelAcesso?.trim()

    if (search) {
      query.set('search', search)
    }

    if (nivelAcesso) {
      query.set('nivel_acesso', nivelAcesso)
    }

    query.set('page', String(params.page))
    query.set('per_page', String(params.perPage))

    return apiRequest<FuncionarioListResponse>(`/usuarios/?${query.toString()}`, {
      method: 'GET',
    })
  },

  async findById(funcionarioId: number): Promise<FuncionarioDetail> {
    return apiRequest<FuncionarioDetail>(`/usuarios/${funcionarioId}`,
      {
        method: 'GET',
      },
    )
  },

  async create(payload: FuncionarioCreatePayload): Promise<Funcionario> {
    return apiRequest<Funcionario>(
      '/usuarios/',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      },
    )
  },

  async update(funcionarioId: number, payload: FuncionarioUpdatePayload): Promise<FuncionarioDetail> {
    return apiRequest<FuncionarioDetail>(
      `/usuarios/${funcionarioId}`,
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