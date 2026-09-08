<script lang="ts">
import { defineComponent } from 'vue'

import AppDataTable from '@/components/AppDataTable.vue'

import { ApiError } from '@/services/api'
import { funcionarioService } from '@/services/funcionarioService'
import { produtoService } from '@/services/produtoService'
import { transacaoService } from '@/services/transacaoService'

import type { DataTableHeader } from '@/types/dataTable'
import type { Funcionario } from '@/types/funcionario'
import type { ProdutoListItem } from '@/types/produto'
import type { TipoMovimentacao, Transacao } from '@/types/transacao'

interface SelectOption {
    title: string
    value: number
}

export default defineComponent({
    name: 'TransacoesView',

    components: {
        AppDataTable,
    },

    data() {
        return {
            transacoes: [] as Transacao[],

            produtos: [] as ProdutoListItem[],
            funcionarios: [] as Funcionario[],

            headers: [
                {
                    key: 'data',
                    title: 'Data/Hora',
                },
                {
                    key: 'movimento',
                    title: 'Movimento',
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
                    key: 'tipo',
                    title: 'Tipo',
                },
                {
                    key: 'usuario_nome',
                    title: 'Responsável'
                },
            ] as DataTableHeader[],

            movimentoOptions: [
                {
                    title: 'Entrada',
                    value: "ENTRADA",
                },
                {
                    title: 'Saída',
                    value: "SAIDA",
                },
            ],

            search: '',

            produtoId: null as number | null,

            movimento: null as TipoMovimentacao | null,

            tipo: '',

            usuarioId: null as number | null,

            quantidade: '',

            dataInicio: '',
            dataFim: '',

            page: 1,
            perPage: 20,
            total: 0,

            loading: false,
            loadingFilters: false,

            errorMessage: '',
        }
    },

    computed: {
        produtoOptions(): SelectOption[] {
            return this.produtos.map((produto) => ({ title: produto.nome, value: produto.id }))
        },

        funcionarioOptions(): SelectOption[] {
            return this.funcionarios.map((funcionario) => ({ title: funcionario.nome, value: funcionario.id }))
        },
    },

    mounted() {
        void this.initialize()
    },

    methods: {
        async initialize(): Promise<void> {
            this.loadingFilters = true
            this.errorMessage = ''

            try {
                await Promise.all([
                    this.loadFilterOptions(),
                    this.loadTransacoes(),
                ])
            } catch (error: unknown) {
                this.handleError(error, 'Não foi possível carregar o histórico de transações.')
            } finally {
                this.loadingFilters = false
            }
        },

        async loadFilterOptions(): Promise<void> {
            const [produtos, funcionarios] = await Promise.all([
                produtoService.list({ page: 1, perPage: 100 }),
                funcionarioService.list({ page: 1, perPage: 100 }),
            ])

            this.produtos = produtos.items
            this.funcionarios = funcionarios.items
        },

        async loadTransacoes(): Promise<void> {
            this.loading = true
            this.errorMessage = ''

            try {
                const response = await transacaoService.list({
                    search: this.search.trim() || undefined,
                    produtoId: this.produtoId ?? undefined,
                    movimento: this.movimento ?? undefined,
                    tipo: this.tipo.trim() || undefined,
                    usuarioId: this.usuarioId ?? undefined,
                    quantidade: this.quantidade.trim() || undefined,
                    dataInicio: this.dataInicio || undefined,
                    dataFim: this.dataFim || undefined,
                    page: this.page,
                    perPage: this.perPage,
                })

                this.transacoes = response.items
                this.total = response.total
            } catch (error: unknown) {
                this.handleError(error, 'Não foi possível carregar as transações.')
            } finally {
                this.loading = false
            }
        },

        async applyFilters(): Promise<void> {
            this.page = 1

            await this.loadTransacoes()
        },

        async clearFilters(): Promise<void> {
            this.search = ''
            this.produtoId = null
            this.movimento = null
            this.tipo = ''
            this.usuarioId = null
            this.quantidade = ''
            this.dataInicio = ''
            this.dataFim = ''

            this.page = 1

            await this.loadTransacoes()
        },

        changePage(page: number): void {
            this.page = page

            void this.loadTransacoes()
        },

        changePerPage(perPage: number): void {
            this.page = 1
            this.perPage = perPage

            void this.loadTransacoes()
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

        formatTipo(value: string): string {
            return value.replaceAll('_', ' ').toLocaleLowerCase('pt-BR').replace(/(^|\s)\S/g, (letter) =>
                letter.toLocaleUpperCase('pt-BR')
            )
        },

        movimentoLabel(value: TipoMovimentacao): string {
            return value === 'ENTRADA'
                ? 'Entrada'
                : 'Saída'
        },

        movimentoColor(value: TipoMovimentacao): string {
            return value === 'ENTRADA'
                ? 'success'
                : 'warning'
        },

        handleError(error: unknown, fallback: string): void {
            if (error instanceof ApiError) {
                this.errorMessage = error.message

                return
            }

            this.errorMessage = fallback
        }
    }
})
</script>

<template>
  <v-container class="py-8">
    <div class="mb-6">
      <h1 class="text-h4 font-weight-bold">
        Histórico de transações
      </h1>

      <p class="text-body-1 text-medium-emphasis mt-2">
        Consulte as movimentações de entrada e saída
        registradas no estoque.
      </p>
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

    <v-card
      rounded="xl"
      variant="outlined"
      class="mb-6"
    >
      <v-card-title class="pa-6 pb-2">
        Filtros
      </v-card-title>

      <v-card-subtitle class="px-6">
        Refine o histórico pelas informações
        da movimentação.
      </v-card-subtitle>

      <v-card-text class="pa-6">
        <v-row>
          <v-col
            cols="12"
            md="4"
          >
            <v-text-field
              v-model="search"
              label="Pesquisar"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="comfortable"
              hide-details
              placeholder="Produto, lote, usuário..."
              @keyup.enter="applyFilters"
            />
          </v-col>

          <v-col
            cols="12"
            md="4"
          >
            <v-select
              v-model="produtoId"
              :items="produtoOptions"
              label="Produto"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
              :loading="loadingFilters"
            />
          </v-col>

          <v-col
            cols="12"
            md="4"
          >
            <v-select
              v-model="movimento"
              :items="movimentoOptions"
              label="Movimento"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
            />
          </v-col>

          <v-col
            cols="12"
            md="4"
          >
            <v-text-field
              v-model="tipo"
              label="Tipo"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
              placeholder="Ex.: Compra, Venda..."
              @keyup.enter="applyFilters"
            />
          </v-col>

          <v-col
            cols="12"
            md="4"
          >
            <v-select
              v-model="usuarioId"
              :items="funcionarioOptions"
              label="Responsável"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
              :loading="loadingFilters"
            />
          </v-col>

          <v-col
            cols="12"
            md="4"
          >
            <v-text-field
              v-model="quantidade"
              label="Quantidade"
              type="number"
              min="0"
              step="0.001"
              variant="outlined"
              density="comfortable"
              hide-details
              @keyup.enter="applyFilters"
            />
          </v-col>

          <v-col
            cols="12"
            md="6"
          >
            <v-text-field
              v-model="dataInicio"
              label="Data inicial"
              type="date"
              variant="outlined"
              density="comfortable"
              hide-details
            />
          </v-col>

          <v-col
            cols="12"
            md="6"
          >
            <v-text-field
              v-model="dataFim"
              label="Data final"
              type="date"
              variant="outlined"
              density="comfortable"
              hide-details
            />
          </v-col>
        </v-row>

        <div class="filter-actions mt-5">
          <v-btn
            variant="text"
            prepend-icon="mdi-filter-off-outline"
            :disabled="loading"
            @click="clearFilters"
          >
            Limpar filtros
          </v-btn>

          <v-btn
            prepend-icon="mdi-filter-outline"
            :loading="loading"
            @click="applyFilters"
          >
            Aplicar filtros
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <app-data-table
      :headers="headers"
      :items="transacoes"
      :actions="[]"
      :loading="loading"
      :page="page"
      :per-page="perPage"
      :total-items="total"
      empty-text="Nenhuma transação encontrada."
      @update:page="changePage"
      @update:per-page="changePerPage"
    >
      <template #item-data="{ item }">
        {{
          formatDateTime(
            item.data,
          )
        }}
      </template>

      <template #item-movimento="{ item }">
        <v-chip
          size="small"
          variant="tonal"
          :color="movimentoColor(
            item.movimento,
          )
          "
        >
          {{
            movimentoLabel(
              item.movimento,
            )
          }}
        </v-chip>
      </template>

      <template #item-produto_nome="{ item }">
        <span class="font-weight-medium">
          {{ item.produto_nome }}
        </span>
      </template>

      <template #item-quantidade="{ item }">
        {{
          formatQuantidade(
            item.quantidade,
          )
        }}
      </template>

      <template #item-tipo="{ item }">
        {{
          formatTipo(
            String(item.tipo),
          )
        }}
      </template>
    </app-data-table>
  </v-container>
</template>

<style scoped>
.filter-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
}

@media (max-width: 700px) {
    .filter-actions {
        flex-direction: column-reverse;
    }

    .filter-actions :deep(.v-btn) {
        width: 100%;
    }
}
</style>