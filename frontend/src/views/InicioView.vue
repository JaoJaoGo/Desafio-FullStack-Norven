<script lang="ts">
import { defineComponent } from 'vue'

import { ApiError } from '@/services/api'
import { fornecedorService } from '@/services/fornecedorService'
import { funcionarioService } from '@/services/funcionarioService'
import { movimentacaoService } from '@/services/movimentacaoService'
import { produtoService } from '@/services/produtoService'

interface ModuleItem {
    title: string
    description: string
    icon: string
    routeName: string
}

interface SummaryItem {
    title: string
    value: number
    description: string
    icon: string
    routeName: string | null
}

interface AlertItem {
    title: string
    value: number
    description: string
    icon: string
    color: string
}

interface DashboardSummary {
    funcionarios: number
    fornecedores: number
    produtos: number
    entradas: number
    saidas: number

    semEstoque: number
    estoqueBaixo: number
    proximoVencimento: number
    vencidos: number
}

export default defineComponent({
    name: 'InicioView',

    data() {
        return {
            loadingDashboard: false,
            dashboardError: '',

            dashboard: {
                funcionarios: 0,
                fornecedores: 0,
                produtos: 0,
                entradas: 0,
                saidas: 0,

                semEstoque: 0,
                estoqueBaixo: 0,
                proximoVencimento: 0,
                vencidos: 0,
            } as DashboardSummary,

            modules: [
                {
                    title: 'Funcionários',
                    description:
                        'Gerencie funcionários, informações de contato e endereços.',
                    icon: 'mdi-account-group-outline',
                    routeName: 'funcionarios',
                },
                {
                    title: 'Fornecedores',
                    description:
                        'Consulte e gerencie fornecedores, contatos e endereços.',
                    icon: 'mdi-truck-outline',
                    routeName: 'fornecedores',
                },
                {
                    title: 'Produtos',
                    description:
                        'Controle produtos, lotes, estoque e movimentações.',
                    icon: 'mdi-package-variant',
                    routeName: 'produtos',
                },
            ] as ModuleItem[],
        }
    },

    computed: {
        summaryItems(): SummaryItem[] {
            return [
                {
                    title: 'Produtos',
                    value: this.dashboard.produtos,
                    description: 'Produtos cadastrados',
                    icon: 'mdi-package-variant-closed',
                    routeName: 'produtos',
                },
                {
                    title: 'Fornecedores',
                    value: this.dashboard.fornecedores,
                    description: 'Fornecedores cadastrados',
                    icon: 'mdi-truck-outline',
                    routeName: 'fornecedores',
                },
                {
                    title: 'Funcionários',
                    value: this.dashboard.funcionarios,
                    description: 'Funcionários cadastrados',
                    icon: 'mdi-account-group-outline',
                    routeName: 'funcionarios',
                },
                {
                    title: 'Entradas',
                    value: this.dashboard.entradas,
                    description: 'Movimentações registradas',
                    icon: 'mdi-package-down',
                    routeName: null,
                },
                {
                    title: 'Saídas',
                    value: this.dashboard.saidas,
                    description: 'Movimentações registradas',
                    icon: 'mdi-package-up',
                    routeName: null,
                },
            ]
        },

        alertItems(): AlertItem[] {
            return [
                {
                    title: 'Sem estoque',
                    value: this.dashboard.semEstoque,
                    description:
                        'Produtos sem saldo disponível',
                    icon: 'mdi-package-variant-remove',
                    color: 'secondary',
                },
                {
                    title: 'Estoque baixo',
                    value: this.dashboard.estoqueBaixo,
                    description:
                        'Produtos que precisam de reposição',
                    icon: 'mdi-package-variant-minus',
                    color: 'warning',
                },
                {
                    title: 'Próximos do vencimento',
                    value: this.dashboard.proximoVencimento,
                    description:
                        'Produtos com lotes próximos da validade',
                    icon: 'mdi-calendar-alert-outline',
                    color: 'warning',
                },
                {
                    title: 'Vencidos',
                    value: this.dashboard.vencidos,
                    description:
                        'Produtos com estoque em lotes vencidos',
                    icon: 'mdi-alert-circle-outline',
                    color: 'error',
                },
            ]
        },

        totalMovimentacoes(): number {
            return (
                this.dashboard.entradas
                + this.dashboard.saidas
            )
        },

        possuiAlertas(): boolean {
            return (
                this.dashboard.semEstoque > 0
                || this.dashboard.estoqueBaixo > 0
                || this.dashboard.proximoVencimento > 0
                || this.dashboard.vencidos > 0
            )
        },
    },

    mounted() {
        void this.loadDashboard()
    },

    methods: {
        async loadDashboard(): Promise<void> {
            this.loadingDashboard = true
            this.dashboardError = ''

            try {
                const [
                    funcionarios,
                    fornecedores,
                    produtos,
                    entradas,
                    saidas,
                    semEstoque,
                    estoqueBaixo,
                    proximoVencimento,
                    vencidos,
                ] = await Promise.all([
                    funcionarioService.list({
                        page: 1,
                        perPage: 1,
                    }),

                    fornecedorService.list({
                        page: 1,
                        perPage: 1,
                    }),

                    produtoService.list({
                        page: 1,
                        perPage: 1,
                    }),

                    movimentacaoService.getEntradaTotal(),

                    movimentacaoService.getSaidaTotal(),

                    produtoService.list({
                        status: 'SEM_ESTOQUE',
                        page: 1,
                        perPage: 1,
                    }),

                    produtoService.list({
                        status: 'ESTOQUE_BAIXO',
                        page: 1,
                        perPage: 1,
                    }),

                    produtoService.list({
                        status: 'PROXIMO_VENCIMENTO',
                        page: 1,
                        perPage: 1,
                    }),

                    produtoService.list({
                        status: 'VENCIDO',
                        page: 1,
                        perPage: 1,
                    }),
                ])

                this.dashboard = {
                    funcionarios:
                        funcionarios.total,

                    fornecedores:
                        fornecedores.total,

                    produtos:
                        produtos.total,

                    entradas,

                    saidas,

                    semEstoque:
                        semEstoque.total,

                    estoqueBaixo:
                        estoqueBaixo.total,

                    proximoVencimento:
                        proximoVencimento.total,

                    vencidos:
                        vencidos.total,
                }
            } catch (error: unknown) {
                if (error instanceof ApiError) {
                    this.dashboardError =
                        error.message
                } else {
                    this.dashboardError =
                        'Não foi possível carregar os indicadores do sistema.'
                }
            } finally {
                this.loadingDashboard = false
            }
        },

        formatNumber(value: number): string {
            return new Intl.NumberFormat(
                'pt-BR',
            ).format(value)
        },

        async openRoute(
            routeName: string | null,
        ): Promise<void> {
            if (!routeName) {
                return
            }

            await this.$router.push({
                name: routeName,
            })
        },

        async openModule(
            module: ModuleItem,
        ): Promise<void> {
            await this.$router.push({
                name: module.routeName,
            })
        },

        async openProdutos(): Promise<void> {
            await this.$router.push({
                name: 'produtos',
            })
        },
    },
})
</script>

<template>
  <v-container class="py-8">
    <v-card
      class="welcome-card mb-8"
      rounded="xl"
      elevation="0"
    >
      <v-card-text class="pa-8 pa-md-10">
        <v-row align="center">
          <v-col
            cols="12"
            md="8"
          >
            <div class="text-overline mb-2">
              Gerenciamento de estoque
            </div>

            <h1 class="text-h3 font-weight-bold mb-4">
              Bem-vindo ao Desafio da Norven
            </h1>

            <p class="text-body-1 welcome-description mb-5">
              Acompanhe os principais indicadores
              do sistema e acesse rapidamente
              os módulos de gerenciamento.
            </p>

            <div class="d-flex flex-wrap ga-3">
              <v-chip
                prepend-icon="mdi-swap-horizontal"
                variant="tonal"
                size="large"
              >
                {{
                  formatNumber(totalMovimentacoes)
                }}
                movimentações
              </v-chip>

              <v-chip
                prepend-icon="mdi-package-variant"
                variant="tonal"
                size="large"
              >
                {{
                  formatNumber(
                    dashboard.produtos,
                  )
                }}
                produtos
              </v-chip>
            </div>
          </v-col>

          <v-col
            cols="12"
            md="4"
            class="d-none d-md-flex justify-end"
          >
            <v-avatar
              size="140"
              variant="tonal"
              class="welcome-icon"
            >
              <v-icon
                icon="mdi-warehouse"
                size="78"
              />
            </v-avatar>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-alert
      v-if="dashboardError"
      type="error"
      variant="tonal"
      closable
      class="mb-6"
      @click:close="dashboardError = ''"
    >
      {{ dashboardError }}
    </v-alert>

    <div class="section-header mb-4">
      <div>
        <h2 class="text-h5 font-weight-bold">
          Visão geral
        </h2>

        <p class="text-body-2 text-medium-emphasis mt-1">
          Principais números registrados no sistema.
        </p>
      </div>

      <v-btn
        icon="mdi-refresh"
        variant="text"
        title="Atualizar indicadores"
        :loading="loadingDashboard"
        @click="loadDashboard"
      />
    </div>

    <v-row class="mb-8">
      <v-col
        v-for="item in summaryItems"
        :key="item.title"
        cols="12"
        sm="6"
        lg="4"
        xl
      >
        <v-card
          class="summary-card h-100"
          rounded="xl"
          variant="outlined"
          :class="{
            'summary-card-clickable':
              item.routeName,
          }"
          @click="openRoute(item.routeName)"
        >
          <v-card-text class="pa-5">
            <div
              class="
                d-flex
                align-start
                justify-space-between
                mb-5
              "
            >
              <v-avatar
                size="46"
                variant="tonal"
              >
                <v-icon
                  :icon="item.icon"
                  size="25"
                />
              </v-avatar>

              <v-progress-circular
                v-if="loadingDashboard"
                indeterminate
                size="22"
                width="2"
              />

              <v-icon
                v-else-if="item.routeName"
                icon="mdi-arrow-top-right"
                size="20"
              />
            </div>

            <div class="summary-value mb-1">
              {{
                loadingDashboard
                  ? '—'
                  : formatNumber(item.value)
              }}
            </div>

            <div class="text-subtitle-1 font-weight-bold">
              {{ item.title }}
            </div>

            <div
              class="
                text-body-2
                text-medium-emphasis
                mt-1
              "
            >
              {{ item.description }}
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <div class="section-header mb-4">
      <div>
        <h2 class="text-h5 font-weight-bold">
          Alertas do estoque
        </h2>

        <p class="text-body-2 text-medium-emphasis mt-1">
          Situações que podem exigir atenção.
        </p>
      </div>

      <v-btn
        variant="text"
        append-icon="mdi-arrow-right"
        @click="openProdutos"
      >
        Ver produtos
      </v-btn>
    </div>

    <v-alert
      v-if="
        !loadingDashboard
          && !possuiAlertas
      "
      type="success"
      variant="tonal"
      icon="mdi-check-circle-outline"
      class="mb-6"
    >
      Nenhum alerta de estoque no momento.
    </v-alert>

    <v-row class="mb-8">
      <v-col
        v-for="item in alertItems"
        :key="item.title"
        cols="12"
        sm="6"
        lg="3"
      >
        <v-card
          class="alert-card h-100"
          rounded="xl"
          variant="outlined"
          @click="openProdutos"
        >
          <v-card-text class="pa-5">
            <div
              class="
                d-flex
                align-start
                justify-space-between
                mb-4
              "
            >
              <v-avatar
                size="44"
                variant="tonal"
                :color="item.color"
              >
                <v-icon
                  :icon="item.icon"
                  size="24"
                />
              </v-avatar>

              <v-chip
                :color="item.color"
                variant="tonal"
                size="small"
              >
                {{
                  loadingDashboard
                    ? '—'
                    : formatNumber(item.value)
                }}
              </v-chip>
            </div>

            <h3
              class="
                text-subtitle-1
                font-weight-bold
                mb-1
              "
            >
              {{ item.title }}
            </h3>

            <p
              class="
                text-body-2
                text-medium-emphasis
              "
            >
              {{ item.description }}
            </p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <div class="mb-4">
      <h2 class="text-h5 font-weight-bold">
        Módulos
      </h2>

      <p class="text-body-2 text-medium-emphasis mt-1">
        Acesse as principais áreas do sistema.
      </p>
    </div>

    <v-row>
      <v-col
        v-for="module in modules"
        :key="module.title"
        cols="12"
        md="4"
      >
        <v-card
          class="module-card h-100"
          rounded="xl"
          variant="outlined"
          @click="openModule(module)"
        >
          <v-card-text class="pa-6">
            <div
              class="
                d-flex
                justify-space-between
                align-start
                mb-5
              "
            >
              <v-avatar
                size="52"
                variant="tonal"
              >
                <v-icon
                  :icon="module.icon"
                  size="28"
                />
              </v-avatar>

              <v-icon
                icon="mdi-arrow-right"
              />
            </div>

            <h3
              class="
                text-h6
                font-weight-bold
                mb-2
              "
            >
              {{ module.title }}
            </h3>

            <p
              class="
                text-body-2
                text-medium-emphasis
              "
            >
              {{ module.description }}
            </p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.welcome-card {
    overflow: hidden;
    background:
        linear-gradient(
            120deg,
            rgba(
                var(--v-theme-primary),
                0.14
            ),
            rgba(
                var(--v-theme-primary),
                0.04
            )
        );
    border:
        1px solid
        rgba(
            var(--v-border-color),
            var(--v-border-opacity)
        );
}

.welcome-description {
    max-width: 680px;
    line-height: 1.7;
    color:
        rgba(
            var(--v-theme-on-surface),
            0.72
        );
}

.welcome-icon {
    background:
        rgba(
            var(--v-theme-primary),
            0.12
        );
}

.section-header {
    display: flex;
    gap: 24px;
    align-items: center;
    justify-content: space-between;
}

.summary-card,
.alert-card,
.module-card {
    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

.summary-card-clickable,
.alert-card,
.module-card {
    cursor: pointer;
}

.summary-card-clickable:hover,
.alert-card:hover,
.module-card:hover {
    transform: translateY(-3px);
    box-shadow:
        0 8px 24px
        rgba(0, 0, 0, 0.08);
}

.summary-value {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
}

@media (max-width: 700px) {
    .section-header {
        flex-direction: column;
        align-items: stretch;
    }
}
</style>