<script lang="ts">
import { defineComponent } from 'vue'

interface ModuleItem {
  title: string
  description: string
  icon: string
  routeName: string | null
  disabled: boolean
}

interface FeatureItem {
  title: string
  description: string
  icon: string
}

export default defineComponent({
  name: 'InicioView',

  data(): {
    modules: ModuleItem[]
    features: FeatureItem[]
  } {
    return {
      modules: [
        {
          title: 'Funcionários',
          description:
            'Gerencie funcionários, informações de contato e endereços.',
          icon: 'mdi-account-group-outline',
          routeName: 'funcionarios',
          disabled: false,
        },
        {
          title: 'Fornecedores',
          description:
            'Consulte e gerencie fornecedores, contatos e endereços.',
          icon: 'mdi-truck-outline',
          routeName: 'fornecedores',
          disabled: false,
        },
        {
          title: 'Produtos',
          description:
            'Controle produtos, lotes, estoque e movimentações.',
          icon: 'mdi-package-variant',
          routeName: 'produtos',
          disabled: false,
        },
      ],

      features: [
        {
          title: 'Controle de estoque',
          description:
            'Acompanhe o saldo disponível dos produtos armazenados.',
          icon: 'mdi-warehouse',
        },
        {
          title: 'Entradas e saídas',
          description:
            'Registre movimentações mantendo o histórico do estoque.',
          icon: 'mdi-swap-horizontal',
        },
        {
          title: 'Rastreabilidade',
          description:
            'Acompanhe produtos por lote, fornecedor e movimentações.',
          icon: 'mdi-text-box-search-outline',
        },
        {
          title: 'Validade',
          description:
            'Identifique produtos vencidos ou próximos do vencimento.',
          icon: 'mdi-calendar-alert-outline',
        },
      ],
    }
  },

  methods: {
    async openModule(module: ModuleItem): Promise<void> {
      if (
        module.disabled ||
        !module.routeName
      ) {
        return
      }

      await this.$router.push({
        name: module.routeName,
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

            <p class="text-body-1 welcome-description">
              Centralize o gerenciamento de funcionários,
              fornecedores, produtos e movimentações de estoque
              em um único sistema.
            </p>
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

    <div class="mb-4">
      <h2 class="text-h5 font-weight-bold">
        Módulos
      </h2>

      <p class="text-body-2 text-medium-emphasis mt-1">
        Acesse as principais áreas do sistema.
      </p>
    </div>

    <v-row class="mb-8">
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
          :class="{
            'module-card-disabled': module.disabled,
          }"
          @click="openModule(module)"
        >
          <v-card-text class="pa-6">
            <div class="d-flex justify-space-between align-start mb-5">
              <v-avatar
                size="52"
                variant="tonal"
              >
                <v-icon
                  :icon="module.icon"
                  size="28"
                />
              </v-avatar>

              <v-chip
                v-if="module.disabled"
                size="small"
                variant="tonal"
              >
                Em breve
              </v-chip>

              <v-icon
                v-else
                icon="mdi-arrow-right"
              />
            </div>

            <h3 class="text-h6 font-weight-bold mb-2">
              {{ module.title }}
            </h3>

            <p class="text-body-2 text-medium-emphasis">
              {{ module.description }}
            </p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <div class="mb-4">
      <h2 class="text-h5 font-weight-bold">
        Gestão do estoque
      </h2>

      <p class="text-body-2 text-medium-emphasis mt-1">
        Recursos que fazem parte do controle de produtos.
      </p>
    </div>

    <v-row>
      <v-col
        v-for="feature in features"
        :key="feature.title"
        cols="12"
        sm="6"
        lg="3"
      >
        <v-card
          height="100%"
          rounded="xl"
          variant="outlined"
        >
          <v-card-text class="pa-5">
            <v-icon
              :icon="feature.icon"
              size="30"
              class="mb-4"
            />

            <h3 class="text-subtitle-1 font-weight-bold mb-2">
              {{ feature.title }}
            </h3>

            <p class="text-body-2 text-medium-emphasis">
              {{ feature.description }}
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
      rgba(var(--v-theme-primary), 0.14),
      rgba(var(--v-theme-primary), 0.04)
    );
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.welcome-description {
  max-width: 680px;
  line-height: 1.7;
  color: rgba(var(--v-theme-on-surface), 0.72);
}

.welcome-icon {
  background:
    rgba(var(--v-theme-primary), 0.12);
}

.module-card {
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.module-card:not(.module-card-disabled) {
  cursor: pointer;
}

.module-card:not(.module-card-disabled):hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px
    rgba(0, 0, 0, 0.08);
}

.module-card-disabled {
  cursor: default;
}
</style>