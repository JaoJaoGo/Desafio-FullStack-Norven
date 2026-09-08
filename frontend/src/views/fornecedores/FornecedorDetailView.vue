<script lang="ts">
import { defineComponent } from 'vue'

import AppDataTable from '@/components/AppDataTable.vue'
import { ApiError } from '@/services/api'
import { fornecedorService } from '@/services/fornecedorService'
import { geografiaService } from '@/services/geografiaService'
import { movimentacaoService } from '@/services/movimentacaoService'

import type { DataTableHeader } from '@/types/dataTable'
import type { FornecedorDetail } from '@/types/fornecedor'
import type { Entrada } from '@/types/movimentacao'

export default defineComponent({
    name: 'FornecedorDetailView',

    components: {
        AppDataTable,
    },

    data() {
        return {
            fornecedor: null as FornecedorDetail | null,

            cidadeNome: '',
            estadoNome: '',
            paisNome: '',

            loading: false,
            errorMessage: '',

            entradas: [] as Entrada[],
            entradaPage: 1,
            entradaPerPage: 20,
            entradaTotal: 0,
            loadingEntradas: false,

            entradaHeaders: [
                {
                    key: 'data_entrada',
                    title: 'Data',
                },
                {
                    key: 'produto_nome',
                    title: 'Produto',
                },
                {
                    key: 'lote_numero',
                    title: "Lote",
                },
                {
                    key: 'quantidade',
                    title: 'Quantidade',
                },
                {
                    key: 'preco_custo_unitario',
                    title: 'Custo unitário',
                },
                {
                    key: 'tipo_entrada',
                    title: 'Tipo',
                },
                {
                    key: 'usuario_nome',
                    title: 'Responsável',
                },
                {
                    key: 'localizacao',
                    title: 'Localização',
                },
            ] as DataTableHeader[],
        }
    },

    computed: {
        fornecedorId(): number | null {
            const id = Number(this.$route.params.id)

            if (!Number.isInteger(id) || id <= 0) {
                return null
            }

            return id
        },
    },

    mounted() {
        void this.initialize()
    },

    methods: {
        async initialize(): Promise<void> {
            const fornecedorId = this.fornecedorId

            if (!fornecedorId) {
                await this.$router.replace({
                    name: 'fornecedores',
                })

                return
            }

            this.loading = true
            this.errorMessage = ''

            try {
                await Promise.all([
                    this.loadFornecedor(),
                    this.loadEntradas(),
                ])
            } catch (error: unknown) {
                this.handleError(error, 'Não foi possível carregar o fornecedor.')
            } finally {
                this.loading = false
            }
        },

        async loadFornecedor(): Promise<void> {
            const fornecedorId = this.fornecedorId

            if (!fornecedorId) {
                return
            }

            const fornecedor = await fornecedorService.findById(fornecedorId)

            this.fornecedor = fornecedor

            const hierarquia = await geografiaService.findCidadeHierarquia(fornecedor.endereco.municipio_id)

            this.cidadeNome = hierarquia.cidade.nome ?? `Cidade ${hierarquia.cidade.id}`

            this.estadoNome = hierarquia.estado.uf ? `${hierarquia.estado.nome ?? ''} (${hierarquia.estado.uf})` :
                hierarquia.estado.nome ?? `Estado ${hierarquia.estado.id}`

            this.paisNome = hierarquia.pais.nome_pt ?? hierarquia.pais.nome ?? hierarquia.pais.sigla ?? `País ${hierarquia.pais.id}`
        },

        async loadEntradas(): Promise<void> {
            const fornecedorId = this.fornecedorId

            if (!fornecedorId) {
                return
            }

            this.loadingEntradas = true

            try {
                const response = await movimentacaoService.listEntradasByFornecedor(fornecedorId, this.entradaPage, this.entradaPerPage)

                this.entradas = response.items
                this.entradaTotal = response.total
            } finally {
                this.loadingEntradas = false
            }
        },

        formatCnpj(cnpj: string): string {
            const digits = cnpj.replace(/\D/g, '')

            if (digits.length !== 14) {
                return cnpj
            }

            return digits.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
        },

        formatCep(cep: string): string {
            const digits = cep.replace(/\D/g, '')

            if (digits.length !== 8) {
                return cep
            }

            return digits.replace(/^(\d{5})(\d{3})$/, '$1-$2')
        },

        formatContato(): string {
            if (!this.fornecedor) {
                return '-'
            }

            const contato = this.fornecedor.contato

            return `+${contato.cod_pais} (${contato.ddd}) ${contato.numero}`
        },

        formatCurrency(value: unknown): string {
            const numeric = Number(value)

            if (!Number.isFinite(numeric)) {
                return '-'
            }

            return new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL',
            }).format(numeric)
        },

        formatQuantidade(value: unknown): string {
            const numeric = Number(value)

            if (!Number.isFinite(numeric)) {
                return '-'
            }

            return new Intl.NumberFormat('pt-BR', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 3,
            }).format(numeric)
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
            }).format(date)
        },

        changeEntradaPage(page: number): void {
            this.entradaPage = page

            void this.loadEntradas()
        },

        changeEntradaPerPage(perPage: number): void {
            this.entradaPage = 1
            this.entradaPerPage = perPage

            void this.loadEntradas()
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
                name: 'fornecedores',
            })
        },

        async editFornecedor(): Promise<void> {
            const fornecedorId = this.fornecedorId

            if (!fornecedorId) {
                return
            }

            await this.$router.push({
                name: 'fornecedor-edit',

                params: {
                    id: fornecedorId,
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
          <h1 class="text-h4 font-weight-bold">
            {{ fornecedor?.nome || 'Fornecedor' }}
          </h1>

          <p class="text-body-1 text-medium-emphasis mt-2">
            Visualize os dados do fornecedor e suas entradas de estoque.
          </p>
        </div>
      </div>

      <v-btn
        prepend-icon="mdi-pencil-outline"
        variant="tonal"
        :disabled="!fornecedor"
        @click="editFornecedor"
      >
        Editar fornecedor
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

    <template v-else-if="fornecedor">
      <v-card
        rounded="xl"
        variant="outlined"
        class="mb-6"
      >
        <v-card-title class="pa-6 pb-2">
          Dados do fornecedor
        </v-card-title>

        <v-card-text class="pa-6">
          <v-row>
            <v-col
              cols="12"
              md="6"
            >
              <div class="detail-label">
                Nome
              </div>
              <div class="detail-value">
                {{ fornecedor.nome }}
              </div>
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <div class="detail-label">
                CNPJ
              </div>
              <div class="detail-value">
                {{ formatCnpj(fornecedor.cnpj) }}
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
              mb="4"
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
              mb="4"
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
              mb="4"
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
              mb="3"
            >
              <div class="detail-label">
                CEP
              </div>
              <div class="detail-value">
                {{ formatCep(fornecedor.endereco.cep) }}
              </div>
            </v-col>
            <v-col
              cols="12"
              mb="6"
            >
              <div class="detail-label">
                Logradouro
              </div>
              <div class="detail-value">
                {{ fornecedor.endereco.logradouro }}
              </div>
            </v-col>
            <v-col
              cols="12"
              mb="3"
            >
              <div class="detail-label">
                Número
              </div>
              <div class="detail-value">
                {{ fornecedor.endereco.numero }}
              </div>
            </v-col>
            <v-col
              cols="12"
              mb="6"
            >
              <div class="detail-label">
                Bairro
              </div>
              <div class="detail-value">
                {{ fornecedor.endereco.bairro }}
              </div>
            </v-col>
            <v-col
              cols="12"
              mb="6"
            >
              <div class="detail-label">
                Complemento
              </div>
              <div class="detail-value">
                {{ fornecedor.endereco.complemento || '-' }}
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <div class="section-header mb-4">
        <div>
          <h2 class="text-h5 font-weight-bold">
            Entradas
          </h2>

          <p class="text-body-2 text-medium-emphasis mt-1">
            Movimentações de entrada vinculadas a este fornecedor.
          </p>
        </div>
      </div>

      <app-data-table
        :headers="entradaHeaders"
        :items="entradas"
        :actions="[]"
        :loading="loadingEntradas"
        :page="entradaPage"
        :per-page="entradaPerPage"
        :total-items="entradaTotal"
        empty-text="Nenhuma entrada registrada para este fornecedor."
        @update:page="changeEntradaPage"
        @update:per-page="changeEntradaPerPage"
      >
        <template #item-data_entrada="{ item }">
          {{ formatDateTime(item.data_entrada) }}
        </template>
        <template #item-quantidade="{ item }">
          {{ formatQuantidade(item.quantidade) }}
        </template>
        <template #item-preco_custo_unitario="{ item }">
          {{ formatCurrency(item.preco_custo_unitario) }}
        </template>
        <template #item-localizacao="{ item }">
          {{ `${item.corredor} / ${item.prateleira} / ${item.secao}` }}
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
    color: rgba(var(--v-theme-on-surface), 0.62);
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