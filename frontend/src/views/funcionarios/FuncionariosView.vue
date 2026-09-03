<script lang="ts">
import { defineComponent } from 'vue'

import AppDataTable from '@/components/AppDataTable.vue'
import { ApiError } from '@/services/api'
import { funcionarioService } from '@/services/funcionarioService'
import { useAuthStore } from '@/stores/auth'

import type { DataTableActionEvent, DataTableHeader } from '@/types/dataTable'
import type { Funcionario, NivelAcesso } from '@/types/funcionario'


export default defineComponent({
  name: 'FuncionariosView',

  components: {
    AppDataTable,
  },

  data() {
    return {
      funcionarios: [] as Funcionario[],

      authStore: useAuthStore(),

      headers: [
        {
          key: 'nome',
          title: 'Nome',
        },
        {
          key: 'email',
          title: 'E-mail',
        },
        {
          key: 'nivel_acesso',
          title: 'Nível de acesso',
        },
      ] as DataTableHeader[],

      search: null as string | null,

      nivelAcessoOptions: [
        {
          title: 'Administrador',
          value: 'administrador',
        },
        {
          title: 'Operador',
          value: 'operador',
        },
      ],

      nivelAcesso: null as NivelAcesso | null,

      page: 1,
      perPage: 20,
      total: 0,

      loading: false,
      errorMessage: '',

      searchTimer: null as ReturnType<typeof setTimeout> | null,

      requestSequence: 0,
    }
  },

  computed: {
    actions() {
      return [
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
          disabled: (
            item: Record<string, unknown>,
          ) => Number(item.id) === this.authStore.currentUserId,
        },
      ]
    },
  },

  watch: {
    search() {
      this.page = 1
      this.scheduleLoad()
    },

    nivelAcesso() {
      this.page = 1
      void this.loadFuncionarios()
    },
  },

  mounted() {
    void this.loadFuncionarios()
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
        void this.loadFuncionarios()
      }, 400)
    },

    async loadFuncionarios(): Promise<void> {
      const requestId = ++this.requestSequence

      this.loading = true
      this.errorMessage = ''

      try {
        const response = await funcionarioService.list(
          {
            search:
              this.search ??
              undefined,

            nivelAcesso:
              this.nivelAcesso ??
              undefined,

            page: this.page,
            perPage: this.perPage,
            },
          )

        if (requestId !== this.requestSequence) {
          return
        }

        this.funcionarios = response.items

        this.total = response.total
      } catch (error: unknown) {
        if (requestId !== this.requestSequence) {
          return
        }

        if (error instanceof ApiError) {
          this.errorMessage = error.message
        } else {
          this.errorMessage = 'Não foi possível carregar os funcionários.'
        }
      } finally {
        if (requestId === this.requestSequence) {
          this.loading = false
        }
      }
    },

    formatNivelAcesso(value: string): string {
      return value.replaceAll('_', ' ')
        .toLocaleLowerCase('pt-BR')
        .replace(/(^|\s)\S/g, (letter) => letter.toLocaleUpperCase('pt-BR'))
    },

    changePage(page: number): void {
      this.page = page

      void this.loadFuncionarios()
    },

    changePerPage(perPage: number): void {
      this.page = 1
      this.perPage = perPage

      void this.loadFuncionarios()
    },

    clearFilters(): void {
      this.search = null
      this.nivelAcesso = null
      this.page = 1
    },

    async createFuncionario():
      Promise<void> {
      await this.$router.push({
        name: 'funcionario-create',
      })
    },

    isCurrentUser(funcionario: Funcionario): boolean {
      return funcionario.id === this.authStore.currentUserId
    },

    async handleAction(event: DataTableActionEvent): Promise<void> {
      const funcionario = event.item as Funcionario

      if (event.action === 'edit') {
        if (this.isCurrentUser(funcionario)) {
          return
        }

        await this.$router.push({
          name: 'funcionario-edit',

          params: {
            id: funcionario.id,
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
          Funcionários
        </h1>

        <p class="text-body-1 text-medium-emphasis mt-2">
          Consulte e gerencie os
          funcionários cadastrados
          no sistema.
        </p>
      </div>

      <v-btn
        prepend-icon="mdi-plus"
        size="large"
        @click="createFuncionario"
      >
        Adicionar funcionário
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
            md="7"
          >
            <v-text-field
              v-model="search"
              label="Pesquisar por nome ou e-mail"
              prepend-inner-icon="mdi-magnify"
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
            <v-select
              v-model="nivelAcesso"
              :items="nivelAcessoOptions"
              label="Nível de acesso"
              prepend-inner-icon="mdi-filter-outline"
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
              title="Limpar filtros"
              @click="clearFilters"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <app-data-table
      :headers="headers"
      :items="funcionarios"
      :actions="actions"
      :loading="loading"
      :page="page"
      :per-page="perPage"
      :total-items="total"
      empty-text="Nenhum funcionário encontrado."
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
              icon="mdi-account-outline"
              size="20"
            />
          </v-avatar>

          <span class="font-weight-medium">
            {{ item.nome }}
          </span>

          <v-chip
            v-if="Number(item.id) === authStore.currentUserId"
            size="x-small"
            variant="tonal"
          >
            Você
          </v-chip>
        </div>
      </template>

      <template #item-nivel_acesso="{ item }">
        <v-chip
          size="small"
          variant="tonal"
        >
          {{ formatNivelAcesso(String(item.nivel_acesso)) }}
        </v-chip>
      </template>
    </app-data-table>
  </v-container>
</template>

<style scoped>
.page-header {
  display: flex;
  gap: 24px;
  align-items: center;
  justify-content:
    space-between;
}

@media (max-width: 700px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>