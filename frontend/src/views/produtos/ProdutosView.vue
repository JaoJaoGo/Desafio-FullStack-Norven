<script lang="ts">
import { defineComponent } from 'vue'

import AppDataTable from '@/components/AppDataTable.vue'
import { ApiError } from '@/services/api'
import { loteService } from '@/services/loteService'
import { produtoService } from '@/services/produtoService'

import type { DataTableAction, DataTableActionEvent, DataTableHeader } from '@/types/dataTable'
import type { Lote } from '@/types/lote'
import type { ProdutoListItem, ProdutoStatus } from '@/types/produto'

export default defineComponent({
  name: 'ProdutosView',

  components: {
    AppDataTable,
  },

  data() {
    return {
      produtos: [] as ProdutoListItem[],

      headers: [
        {
          key: 'nome',
          title: 'Nome',
        },
        {
          key: 'preco_venda_atual',
          title: 'Preço',
        },
        {
          key: 'validade',
          title: 'Validade',
        },
        {
          key: 'status',
          title: 'Status',
        },
      ] as DataTableHeader[],

      actions: [
        {
          key: 'view',
          title: 'Visualizar',
          icon: 'mdi-eye-outline',
        },
        {
          key: 'edit',
          title: 'Editar',
          icon: 'mdi-pencil-outline',
        },
      ] as DataTableAction[],

      statusOptions: [
        {
          title: 'Sem estoque',
          value: 'SEM_ESTOQUE',
        },
        {
          title: 'Vencido',
          value: 'VENCIDO',
        },
        {
          title: 'Próximo do vencimento',
          value: 'PROXIMO_VENCIMENTO',
        },
        {
          title: 'Estoque baixo',
          value: 'ESTOQUE_BAIXO',
        },
        {
          title: 'OK',
          value: 'OK',
        },
      ],

      nome: null as string | null,

      statusProduto: null as ProdutoStatus | null,

      precoMin: null as string | null,

      precoMax: null as string | null,

      page: 1,
      perPage: 20,
      total: 0,

      loading: false,
      errorMessage: '',

      searchTimer: null as ReturnType<typeof setTimeout> | null,

      requestSequence: 0,
      filtersPaused: false,

      validadeDialog: false,
      validadeLoading: false,
      validadeProdutoNome: '',
      validadeLotes: [] as Lote[],
    }
  },

  watch: {
    nome() {
      if (!this.filtersPaused) {
        this.page = 1
        this.scheduleLoad()
      }
    },

    statusProduto() {
      if (!this.filtersPaused) {
        this.page = 1
        void this.loadProdutos()
      }
    },

    precoMin() {
      if (!this.filtersPaused) {
        this.page = 1
        this.scheduleLoad()
      }
    },

    precoMax() {
      if (!this.filtersPaused) {
        this.page = 1
        this.scheduleLoad()
      }
    },
  },

  mounted() {
    void this.loadProdutos()
  },

  beforeUnmount() {
    if (this.searchTimer) {
      clearTimeout(this.searchTimer)
    }
  },

  methods: {
    scheduleLoad(): void {
      if (this.searchTimer) {
        clearTimeout(this.searchTimer)
      }

      this.searchTimer = setTimeout(() => {
        void this.loadProdutos()
      }, 400)
    },

    normalizePriceFilter(value: string | null): string | undefined {
      const normalized = value?.trim().replace(',', '.')

      if (!normalized) {
        return undefined
      }

      if (!/^\d+(\.\d{1,2})?$/.test(normalized)) {
        return undefined
      }

      return normalized
    },

    async loadProdutos(): Promise<void> {
      const requestId = ++this.requestSequence

      this.errorMessage = ''

      const precoMinRaw = this.precoMin?.trim()

      const precoMaxRaw = this.precoMax?.trim()

      const precoMin = this.normalizePriceFilter(this.precoMin)

      const precoMax = this.normalizePriceFilter(this.precoMax)

      if ((precoMinRaw && !precoMin) || (precoMaxRaw && !precoMax)) {
        this.errorMessage = 'Informe valores de preço válidos.'

        return
      }

      if (precoMin && precoMax && Number(precoMin) > Number(precoMax)) {
        this.errorMessage = 'O preço mínimo não pode ser maior que o preço máximo.'

        return
      }

      this.loading = true

      try {
        const response = await produtoService.list({
          nome: this.nome ?? undefined,

          status: this.statusProduto ?? undefined,

          precoMin,
          precoMax,

          page: this.page,

          perPage: this.perPage,
        })

        if (requestId !== this.requestSequence) {
          return
        }

        this.produtos = response.items

        this.total = response.total
      } catch (error: unknown) {
        if (requestId !== this.requestSequence) {
          return
        }

        if (error instanceof ApiError) {
          this.errorMessage = error.message
        } else {
          this.errorMessage = 'Não foi possível carregar os produtos.'
        }
      } finally {
        if (requestId === this.requestSequence) {
          this.loading = false
        }
      }
    },

    formatCurrency(value: unknown): string {
      const numeric = Number(value)

      if (!Number.isFinite(numeric)) {
        return '-'
      }

      return new Intl.NumberFormat(
        'pt-BR',
        {
          style: 'currency',
          currency: 'BRL',
        },
      ).format(numeric)
    },

    formatDate(value: unknown): string {
      if (!value) {
        return '-'
      }

      const parts = String(value).split('-')

      if (parts.length !== 3) {
        return String(value)
      }

      return `${parts[2]}/${parts[1]}/${parts[0]}`
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

    changePage(page: number): void {
      this.page = page
      void this.loadProdutos()
    },

    changePerPage(perPage: number): void {
      this.page = 1
      this.perPage = perPage

      void this.loadProdutos()
    },

    async clearFilters(): Promise<void> {
      if (this.searchTimer) {
        clearTimeout(this.searchTimer)
      }

      this.filtersPaused = true

      this.nome = null
      this.statusProduto = null
      this.precoMin = null
      this.precoMax = null
      this.page = 1

      await this.$nextTick()

      this.filtersPaused = false

      await this.loadProdutos()
    },

    async createProduto(): Promise<void> {
      await this.$router.push({
        name: 'produto-create',
      })
    },

    async openValidades(produto: ProdutoListItem): Promise<void> {
      this.validadeDialog = true
      this.validadeLoading = true

      this.validadeProdutoNome = produto.nome

      this.validadeLotes = []

      try {
        this.validadeLotes = await loteService.listAllByProduct(produto.id)
      } catch (error: unknown) {
        this.validadeDialog = false

        if (error instanceof ApiError) {
          this.errorMessage = error.message
        } else {
          this.errorMessage = 'Não foi possível carregar as datas dos lotes.'
        }
      } finally {
        this.validadeLoading = false
      }
    },

    async handleAction(event: DataTableActionEvent): Promise<void> {
      const produto = event.item as ProdutoListItem

      if (event.action === 'view') {
        await this.$router.push({
          name: 'produto-detail',

          params: {
            id: produto.id,
          },
        })

        return
      }

      if (event.action === 'edit') {
        await this.$router.push({
          name: 'produto-edit',

          params: {
            id: produto.id,
          },
        })
      }
    },
  },
})
</script>

<template>
  <v-container class="py-8">
    <div class="page-header mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">
          Produtos
        </h1>

        <p class="text-body-1 text-medium-emphasis mt-2">
          Consulte e gerencie os produtos cadastrados
          no sistema.
        </p>
      </div>

      <v-btn
        prepend-icon="mdi-plus"
        size="large"
        @click="createProduto"
      >
        Adicionar produto
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

    <v-card
      rounded="xl"
      variant="outlined"
      class="mb-5"
    >
      <v-card-text class="pa-5">
        <v-row align="center">
          <v-col
            cols="12"
            lg="4"
          >
            <v-text-field
              v-model="nome"
              label="Pesquisar por nome"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
            />
          </v-col>

          <v-col
            cols="12"
            sm="6"
            lg="3"
          >
            <v-select
              v-model="statusProduto"
              :items="statusOptions"
              label="Status"
              prepend-inner-icon="mdi-filter-outline"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
            />
          </v-col>

          <v-col
            cols="12"
            sm="6"
            lg="2"
          >
            <v-text-field
              v-model="precoMin"
              label="Preço mínimo"
              prefix="R$"
              inputmode="decimal"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
            />
          </v-col>

          <v-col
            cols="12"
            sm="6"
            lg="2"
          >
            <v-text-field
              v-model="precoMax"
              label="Preço máximo"
              prefix="R$"
              inputmode="decimal"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
            />
          </v-col>

          <v-col
            cols="12"
            sm="6"
            lg="1"
            class="d-flex justify-end"
          >
            <v-btn
              icon="mdi-filter-off-outline"
              variant="text"
              title="Limpar filtros"
              @click="clearFilters"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <app-data-table
      :headers="headers"
      :items="produtos"
      :actions="actions"
      :loading="loading"
      :page="page"
      :per-page="perPage"
      :total-items="total"
      empty-text="Nenhum produto encontrado."
      @update:page="changePage"
      @update:per-page="changePerPage"
      @action="handleAction"
    >
      <template #item-nome="{ item }">
        <div class="d-flex align-center ga-3 py-2">
          <v-avatar
            size="36"
            variant="tonal"
          >
            <v-icon
              icon="mdi-package-variant"
              size="20"
            />
          </v-avatar>

          <div>
            <div class="font-weight-medium">
              {{ item.nome }}
            </div>

            <div class="text-caption text-medium-emphasis">
              {{ item.cod_idt }}
            </div>
          </div>
        </div>
      </template>

      <template #item-preco_venda_atual="{ item }">
        <span class="font-weight-medium">
          {{
            formatCurrency(
              item.preco_venda_atual,
            )
          }}
        </span>
      </template>

      <template #item-validade="{ item }">
        <v-btn
          v-if="
            Number(item.quantidade_lotes) > 1
          "
          size="small"
          variant="tonal"
          prepend-icon="mdi-calendar-multiple"
          @click.stop="
            openValidades(
              item as ProdutoListItem,
            )
          "
        >
          Ver datas
        </v-btn>

        <span
          v-else
          :class="{
            'text-medium-emphasis':
              !item.validade,
          }"
        >
          {{
            formatDate(
              item.validade,
            )
          }}
        </span>
      </template>

      <template #item-status="{ item }">
        <div class="d-flex flex-wrap ga-2 py-2">
          <v-chip
            v-for="produtoStatus in (
            item.statuses as ProdutoStatus[]
            )"
            :key="produtoStatus"
            size="small"
            variant="tonal"
            :color="statusColor(
              produtoStatus,
            )
            "
          >
            {{
              formatStatus(
                produtoStatus,
              )
            }}
          </v-chip>
        </div>
      </template>
    </app-data-table>

    <v-dialog
      v-model="validadeDialog"
      max-width="600"
    >
      <v-card rounded="xl">
        <v-card-title class="pa-6 pb-2">
          Datas de validade
        </v-card-title>

        <v-card-subtitle class="px-6">
          {{ validadeProdutoNome }}
        </v-card-subtitle>

        <v-card-text class="pa-6">
          <v-progress-linear
            v-if="validadeLoading"
            indeterminate
          />

          <v-table v-else>
            <thead>
              <tr>
                <th>Lote</th>
                <th>Data de validade</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="lote in validadeLotes"
                :key="lote.id"
              >
                <td>
                  {{ lote.numero }}
                </td>

                <td>
                  {{
                    formatDate(
                      lote.data_validade,
                    )
                  }}
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>

        <v-card-actions class="px-6 pb-6">
          <v-spacer />

          <v-btn @click="validadeDialog = false">
            Fechar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.page-header {
  display: flex;
  gap: 24px;
  align-items: center;
  justify-content: space-between;
}

@media (max-width: 700px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>