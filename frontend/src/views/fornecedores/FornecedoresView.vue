<script lang="ts">
import { defineComponent } from 'vue'

import AppDataTable from '@/components/AppDataTable.vue'
import { ApiError } from '@/services/api'
import { fornecedorService } from '@/services/fornecedorService'
import type { DataTableAction, DataTableActionEvent, DataTableHeader } from '@/types/dataTable'
import type { Fornecedor } from '@/types/fornecedor'

export default defineComponent({
  name: 'FornecedoresView',

  components: { AppDataTable },

  data() {
    return {
      fornecedores: [] as Fornecedor[],

      headers: [
        {
          key: 'nome',
          title: 'Nome',
        },
        {
          key: 'cnpj',
          title: 'CNPJ',
        },
      ] as DataTableHeader[],

      actions: [
        {
          key: 'view',
          title: 'Visualizar',
          icon: 'mdi-eye-outline',
          disabled: true,
        },
        {
          key: 'edit',
          title: 'Editar',
          icon: 'mdi-pencil-outline',
        },
      ] as DataTableAction[],

      search: null as string | null,

      page: 1,
      perPage: 20,
      total: 0,

      loading: false,
      errorMessage: '',

      searchTimer: null as ReturnType<typeof setTimeout> | null,

      requestSequence: 0,
    }
  },

  watch: {
    search() {
      this.page = 1
      this.scheduleLoad()
    },
  },

  mounted() {
    void this.loadFornecedores()
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
        void this.loadFornecedores()
      }, 400)
    },

    async loadFornecedores(): Promise<void> {
      const requestId = ++this.requestSequence

      this.loading = true
      this.errorMessage = ''

      try {
        const response =
          await fornecedorService.list(
            {
              search: this.search ?? undefined,
              page: this.page,
              perPage: this.perPage,
            },
          )

        if (requestId !== this.requestSequence) {
          return
        }

        this.fornecedores = response.items

        this.total = response.total
      } catch (error: unknown) {
        if (requestId !== this.requestSequence) {
          return
        }

        if (error instanceof ApiError) {
          this.errorMessage = error.message
        } else {
          this.errorMessage = 'Não foi possível carregar os fornecedores.'
        }
      } finally {
        if (requestId === this.requestSequence) {
          this.loading = false
        }
      }
    },

    formatCnpj(cnpj: string): string {
      const digits = cnpj.replace(/\D/g, '')

      if (digits.length !== 14) {
        return cnpj
      }

      return digits.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
    },

    changePage(page: number): void {
      this.page = page

      void this.loadFornecedores()
    },

    changePerPage(perPage: number): void {
      this.page = 1
      this.perPage = perPage

      void this.loadFornecedores()
    },

    clearSearch(): void {
      this.search = null
      this.page = 1
    },

    async createFornecedor(): Promise<void> {
      await this.$router.push({
        name: 'fornecedor-create',
      })
    },

    async handleAction(event: DataTableActionEvent): Promise<void> {
      const fornecedor = event.item as Fornecedor

      if (event.action === 'edit') {
        await this.$router.push({
          name: 'fornecedor-edit',

          params: {
            id: fornecedor.id,
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
          Fornecedores
        </h1>

        <p class="text-body-1 text-medium-emphasis mt-2">
          Consulte e gerencie os fornecedores cadastrados
          no sistema.
        </p>
      </div>

      <v-btn
        prepend-icon="mdi-plus"
        size="large"
        @click="createFornecedor"
      >
        Adicionar fornecedor
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
            md="11"
          >
            <v-text-field
              v-model="search"
              label="Pesquisar por nome ou CNPJ"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
            />
          </v-col>

          <v-col
            cols="12"
            md="1"
            class="d-flex justify-end"
          >
            <v-btn
              icon="mdi-filter-off-outline"
              variant="text"
              title="Limpar pesquisa"
              @click="clearSearch"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <app-data-table
      :headers="headers"
      :items="fornecedores"
      :actions="actions"
      :loading="loading"
      :page="page"
      :per-page="perPage"
      :total-items="total"
      empty-text="Nenhum fornecedor encontrado."
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
              icon="mdi-truck-outline"
              size="20"
            />
          </v-avatar>

          <span class="font-weight-medium">
            {{ item.nome }}
          </span>
        </div>
      </template>

      <template #item-cnpj="{ item }">
        <span class="font-weight-medium">
          {{ formatCnpj(String(item.cnpj)) }}
        </span>
      </template>
    </app-data-table>
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