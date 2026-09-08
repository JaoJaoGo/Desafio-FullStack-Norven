<script lang="ts">
import { defineComponent } from 'vue'

import AppDataTable from '@/components/AppDataTable.vue'
import { ApiError } from '@/services/api'
import { funcionarioService } from '@/services/funcionarioService'
import { geografiaService } from '@/services/geografiaService'
import { movimentacaoService } from '@/services/movimentacaoService'
import { produtoService } from '@/services/produtoService'
import { useAuthStore } from '@/stores/auth'

import type { DataTableHeader } from '@/types/dataTable'
import type { FuncionarioDetail, NivelAcesso } from '@/types/funcionario'
import type { Saida } from '@/types/movimentacao'
import type { ProdutoListItem, ProdutoStatus } from '@/types/produto'

export default defineComponent({
    name: 'FuncionarioDetailView',

    components: {
        AppDataTable,
    },

    data() {
        return {
            authStore: useAuthStore(),

            funcionario: null as FuncionarioDetail | null,

            cidadeNome: '',
            estadoNome: '',
            paisNome: '',

            loading: false,
            errorMessage: '',

            produtos: [] as ProdutoListItem[],
            produtoPage: 1,
            produtoPerPage: 10,
            produtoTotal: 0,
            loadingProdutos: false,

            saidas: [] as Saida[],
            saidaPage: 1,
            saidaPerPage: 10,
            saidaTotal: 0,
            loadingSaidas: false,

            produtoHeaders: [
                {
                    key: 'cod_idt',
                    title: 'Código',
                },
                {
                    key: 'nome',
                    title: 'Nome',
                },
                {
                    key: 'categoria',
                    title: 'Categoria',
                },
                {
                    key: 'preco_venda_atual',
                    title: 'Preço',
                },
                {
                    key: 'status',
                    title: 'Status',
                },
            ] as DataTableHeader[],

            saidaHeaders: [
                {
                    key: 'data_saida',
                    title: 'Data',
                },
                {
                    key: 'produto_nome',
                    title: 'Produto',
                },
                {
                    key: 'lote_numero',
                    title: 'Lote',
                },
                {
                    key: 'quantidade',
                    title: 'Quantidade',
                },
                {
                    key: 'tipo_saida',
                    title: 'Tipo',
                },
                {
                    key: 'preco_venda_unitario',
                    title: 'Preço',
                },
            ] as DataTableHeader[],
        }
    },

    computed: {
        funcionarioId(): number | null {
            const id = Number(this.$route.params.id)

            if (!Number.isInteger(id) || id <= 0) {
                return null
            }

            return id
        },

        isCurrentUser(): boolean {
            return (this.funcionarioId === this.authStore.currentUserId)
        },
    },

    mounted() {
        void this.initialize()
    },

    methods: {
        async initialize(): Promise<void> {
            const funcionarioId = this.funcionarioId

            if (!funcionarioId) {
                await this.$router.replace({
                    name: 'funcionarios',
                })

                return
            }

            this.loading = true
            this.errorMessage = ''

            try {
                await Promise.all([
                    this.loadFuncionario(),
                    this.loadProdutos(),
                    this.loadSaidas(),
                ])
            } catch (error: unknown) {
                this.handleError(error, 'Não foi possível carregar o funcionário.')
            } finally {
                this.loading = false
            }
        },

        async loadFuncionario(): Promise<void> {
            const funcionarioId = this.funcionarioId

            if (!funcionarioId) {
                return
            }

            const funcionario = await funcionarioService.findById(funcionarioId)

            this.funcionario = funcionario

            const hierarquia = await geografiaService.findCidadeHierarquia(funcionario.endereco.municipio_id)

            this.cidadeNome = hierarquia.cidade.nome ?? `Cidade ${hierarquia.cidade.id}`

            this.estadoNome = hierarquia.estado.uf ? `${hierarquia.estado.nome ?? ''} (${hierarquia.estado.uf})`
                    : hierarquia.estado.nome ?? `Estado ${hierarquia.estado.id}`

            this.paisNome = hierarquia.pais.nome_pt ?? hierarquia.pais.nome ?? hierarquia.pais.sigla ?? `País ${hierarquia.pais.id}`
        },

        async loadProdutos(): Promise<void> {
            const funcionarioId = this.funcionarioId

            if (!funcionarioId) {
                return
            }

            this.loadingProdutos = true

            try {
                const response = await produtoService.list({
                        usuarioId: funcionarioId,
                        page: this.produtoPage,
                        perPage: this.produtoPerPage,
                    })

                this.produtos = response.items
                this.produtoTotal = response.total
            } finally {
                this.loadingProdutos = false
            }
        },

        async loadSaidas(): Promise<void> {
            const funcionarioId = this.funcionarioId

            if (!funcionarioId) {
                return
            }

            this.loadingSaidas = true

            try {
                const response = await movimentacaoService.listSaidasByFuncionario(funcionarioId, this.saidaPage, this.saidaPerPage)

                this.saidas = response.items
                this.saidaTotal = response.total
            } finally {
                this.loadingSaidas = false
            }
        },

        formatNivelAcesso(value: NivelAcesso): string {
            const labels: Record<NivelAcesso, string> = {
                    administrador: 'Administrador',
                    operador: 'Operador',
                }

            return labels[value]
        },

        formatContato(): string {
            if (!this.funcionario) {
                return '-'
            }

            const contato = this.funcionario.contato

            return `+${contato.cod_pais} (${contato.ddd}) ${contato.numero}`
        },

        formatCep(value: string): string {
            const digits = value.replace(/\D/g, '')

            if (digits.length !== 8) {
                return value
            }

            return digits.replace(/^(\d{5})(\d{3})$/, '$1-$2')
        },

        formatCurrency(value: unknown): string {
            const numeric = Number(value)

            if (!Number.isFinite(numeric)) {
                return '-'
            }

            return new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL',
                },
            ).format(numeric)
        },

        formatQuantidade(value: unknown): string {
            const numeric = Number(value)

            if (!Number.isFinite(numeric)) {
                return '-'
            }

            return new Intl.NumberFormat('pt-BR', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 3,
                },
            ).format(numeric)
        },

        formatDateTime(value: unknown): string {
            if (!value) {
                return '-'
            }

            const date = new Date(String(value))

            if (Number.isNaN(date.getTime())) {
                return String(value)
            }

            return new Intl.DateTimeFormat('pt-BR', {
                    dateStyle: 'short',
                    timeStyle: 'short',
                },
            ).format(date)
        },

        formatTipoSaida(value: string): string {
            return value.replaceAll('_', ' ').toLocaleLowerCase('pt-BR').replace(/(^|\s)\S/g, (letter) => letter.toLocaleUpperCase('pt-BR'))
        },

        formatStatus(status: ProdutoStatus): string {
            const labels: Record<ProdutoStatus, string> = {
                    SEM_ESTOQUE: 'Sem estoque',
                    VENCIDO: 'Vencido',
                    PROXIMO_VENCIMENTO: 'Próximo do vencimento',
                    ESTOQUE_BAIXO: 'Estoque baixo',
                    OK: 'OK',
                }

            return labels[status]
        },

        statusColor(status: ProdutoStatus): string {
            const colors: Record<ProdutoStatus, string> = {
                    SEM_ESTOQUE: 'secondary',
                    VENCIDO: 'error',
                    PROXIMO_VENCIMENTO: 'warning',
                    ESTOQUE_BAIXO: 'warning',
                    OK: 'success',
                }

            return colors[status]
        },

        changeProdutoPage(page: number): void {
            this.produtoPage = page

            void this.loadProdutos()
        },

        changeProdutoPerPage(perPage: number): void {
            this.produtoPage = 1
            this.produtoPerPage = perPage

            void this.loadProdutos()
        },

        changeSaidaPage(page: number): void {
            this.saidaPage = page

            void this.loadSaidas()
        },

        changeSaidaPerPage(perPage: number): void {
            this.saidaPage = 1
            this.saidaPerPage = perPage

            void this.loadSaidas()
        },

        handleError(error: unknown, fallback: string): void {
            if (error instanceof ApiError) {
                this.errorMessage = error.message

                return
            }

            this.errorMessage = fallback
        },

        async goBack(): Promise<void> {
            await this.$router.push({
                name: 'funcionarios',
            })
        },

        async editFuncionario(): Promise<void> {
            const funcionarioId = this.funcionarioId

            if (!funcionarioId || this.isCurrentUser) {
                return
            }

            await this.$router.push({
                name: 'funcionario-edit',

                params: {
                    id: funcionarioId,
                },
            })
        },
    },
})
</script>

<template>
  <v-container class="py-8">
    <div class="page-header mb-6">
      <div class="d-flex align-center ga-4">
        <v-btn
          icon="mdi-arrow-left"
          variant="text"
          title="Voltar"
          @click="goBack"
        />

        <div>
          <div class="d-flex align-center ga-2">
            <h1 class="text-h4 font-weight-bold">
              {{ funcionario?.nome || 'Funcionário' }}
            </h1>

            <v-chip
              v-if="isCurrentUser"
              size="small"
              variant="tonal"
            >
              Você
            </v-chip>
          </div>

          <p class="text-body-1 text-medium-emphasis mt-2">
            Visualize os dados, produtos cadastrados
            e saídas realizadas por este funcionário.
          </p>
        </div>
      </div>

      <v-btn
        prepend-icon="mdi-pencil-outline"
        variant="tonal"
        :disabled="!funcionario || isCurrentUser"
        @click="editFuncionario"
      >
        Editar funcionário
      </v-btn>
    </div>

    <v-alert
      v-if="errorMessage"
      type="error"
      variant="tonal"
      closable
      class="mb-6"
      @click:close="errorMessage = ''"
    >
      {{ errorMessage }}
    </v-alert>

    <v-progress-linear
      v-if="loading"
      indeterminate
    />

    <template v-else-if="funcionario">
      <v-card
        rounded="xl"
        variant="outlined"
        class="mb-6"
      >
        <v-card-title class="pa-6 pb-2">
          Dados do funcionário
        </v-card-title>

        <v-card-text class="pa-6">
          <v-row>
            <v-col
              cols="12"
              md="4"
            >
              <div class="detail-label">
                Nome
              </div>

              <div class="detail-value">
                {{ funcionario.nome }}
              </div>
            </v-col>

            <v-col
              cols="12"
              md="4"
            >
              <div class="detail-label">
                E-mail
              </div>

              <div class="detail-value">
                {{ funcionario.email }}
              </div>
            </v-col>

            <v-col
              cols="12"
              md="4"
            >
              <div class="detail-label">
                Nível de acesso
              </div>

              <div class="detail-value">
                <v-chip
                  size="small"
                  variant="tonal"
                >
                  {{
                    formatNivelAcesso(
                      funcionario.nivel_acesso,
                    )
                  }}
                </v-chip>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <v-card
        rounded="xl"
        variant="outlined"
        class="mb-6"
      >
        <v-card-title class="pa-6 pb-2">
          Contato
        </v-card-title>

        <v-card-text class="pa-6">
          <v-row>
            <v-col
              cols="12"
              md="6"
            >
              <div class="detail-label">
                Telefone
              </div>

              <div class="detail-value">
                {{ formatContato() }}
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <v-card
        rounded="xl"
        variant="outlined"
        class="mb-8"
      >
        <v-card-title class="pa-6 pb-2">
          Endereço
        </v-card-title>

        <v-card-text class="pa-6">
          <v-row>
            <v-col
              cols="12"
              md="4"
            >
              <div class="detail-label">
                País
              </div>

              <div class="detail-value">
                {{ paisNome }}
              </div>
            </v-col>

            <v-col
              cols="12"
              md="4"
            >
              <div class="detail-label">
                Estado
              </div>

              <div class="detail-value">
                {{ estadoNome }}
              </div>
            </v-col>

            <v-col
              cols="12"
              md="4"
            >
              <div class="detail-label">
                Cidade
              </div>

              <div class="detail-value">
                {{ cidadeNome }}
              </div>
            </v-col>

            <v-col
              cols="12"
              md="3"
            >
              <div class="detail-label">
                CEP
              </div>

              <div class="detail-value">
                {{
                  formatCep(
                    funcionario.endereco.cep,
                  )
                }}
              </div>
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <div class="detail-label">
                Logradouro
              </div>

              <div class="detail-value">
                {{ funcionario.endereco.logradouro }}
              </div>
            </v-col>

            <v-col
              cols="12"
              md="3"
            >
              <div class="detail-label">
                Número
              </div>

              <div class="detail-value">
                {{ funcionario.endereco.numero }}
              </div>
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <div class="detail-label">
                Bairro
              </div>

              <div class="detail-value">
                {{ funcionario.endereco.bairro }}
              </div>
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <div class="detail-label">
                Complemento
              </div>

              <div class="detail-value">
                {{
                  funcionario.endereco.complemento
                    || '-'
                }}
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <div class="section-header mb-4">
        <div>
          <h2 class="text-h5 font-weight-bold">
            Produtos cadastrados
          </h2>

          <p class="text-body-2 text-medium-emphasis mt-1">
            Produtos cujo cadastro foi realizado
            por este funcionário.
          </p>
        </div>
      </div>

      <app-data-table
        :headers="produtoHeaders"
        :items="produtos"
        :actions="[]"
        :loading="loadingProdutos"
        :page="produtoPage"
        :per-page="produtoPerPage"
        :total-items="produtoTotal"
        empty-text="Nenhum produto cadastrado por este funcionário."
        class="mb-8"
        @update:page="changeProdutoPage"
        @update:per-page="changeProdutoPerPage"
      >
        <template #item-preco_venda_atual="{ item }">
          {{
            formatCurrency(
              item.preco_venda_atual,
            )
          }}
        </template>

        <template #item-status="{ item }">
          <div class="d-flex flex-wrap ga-1">
            <v-chip
              v-for="statusProduto in item.statuses"
              :key="statusProduto"
              size="small"
              variant="tonal"
              :color="statusColor(statusProduto)"
            >
              {{ formatStatus(statusProduto) }}
            </v-chip>
          </div>
        </template>
      </app-data-table>

      <div class="section-header mb-4">
        <div>
          <h2 class="text-h5 font-weight-bold">
            Saídas realizadas
          </h2>

          <p class="text-body-2 text-medium-emphasis mt-1">
            Movimentações de saída registradas
            por este funcionário.
          </p>
        </div>
      </div>

      <app-data-table
        :headers="saidaHeaders"
        :items="saidas"
        :actions="[]"
        :loading="loadingSaidas"
        :page="saidaPage"
        :per-page="saidaPerPage"
        :total-items="saidaTotal"
        empty-text="Nenhuma saída registrada por este funcionário."
        @update:page="changeSaidaPage"
        @update:per-page="changeSaidaPerPage"
      >
        <template #item-data_saida="{ item }">
          {{
            formatDateTime(
              item.data_saida,
            )
          }}
        </template>

        <template #item-quantidade="{ item }">
          {{
            formatQuantidade(
              item.quantidade,
            )
          }}
        </template>

        <template #item-tipo_saida="{ item }">
          {{
            formatTipoSaida(
              String(item.tipo_saida),
            )
          }}
        </template>

        <template #item-preco_venda_unitario="{ item }">
          {{
            item.preco_venda_unitario !== null
              ? formatCurrency(
                item.preco_venda_unitario,
              )
              : '-'
          }}
        </template>
      </app-data-table>
    </template>
  </v-container>
</template>

<style scoped>
.page-header,
.section-header {
    display: flex;
    gap: 24px;
    align-items: center;
    justify-content: space-between;
}

.detail-label {
    margin-bottom: 4px;
    font-size: 0.78rem;
    color:
        rgba(
            var(--v-theme-on-surface),
            0.62
        );
}

.detail-value {
    font-weight: 500;
}

@media (max-width: 700px) {
    .page-header,
    .section-header {
        flex-direction: column;
        align-items: stretch;
    }
}
</style>