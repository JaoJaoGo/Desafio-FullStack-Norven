<script lang="ts">
import { defineComponent } from 'vue'

interface NavigationItem {
    title: string
    icon: string
    routeName: string | null
    disabled: boolean
}

export default defineComponent({
    name: 'AppSidebar',

    props: {
        modelValue: {
            type: Boolean,
            required: true,
        },
    },

    emits: [
        'update:modelValue',
    ],

    data(): {
        navigationItems: NavigationItem[]
    } {
        return {
            navigationItems: [
                {
                    title: 'Início',
                    icon: 'mdi-home-outline',
                    routeName: 'inicio',
                    disabled: false,
                },
                {
                  title: "Funcionários",
                  icon: "mdi-account-group-outline",
                  routeName: 'funcionarios',
                  disabled: false,
                },
                {
                  title: "Fornecedores",
                  icon: "mdi-truck-outline",
                  routeName: null,
                  disabled: true,
                },
                {
                  title: "Produtos",
                  icon: "mdi-package-variant",
                  routeName: null,
                  disabled: true,
                },
            ],
        }
    },
})
</script>

<template>
  <v-navigation-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="sidebar-brand">
      <v-avatar
        size="44"
        variant="tonal"
      >
        <v-icon
          icon="mdi-package-variant-closed"
          size="26"
        />
      </v-avatar>

      <div>
        <div class="text-subtitle-1 font-weight-bold">
          Norven
        </div>

        <div class="text-caption text-medium-emphasis">
          Controle de Estoque
        </div>
      </div>
    </div>

    <v-divider />

    <v-list
      nav
      density="comfortable"
      class="pa-3"
    >
      <v-list-item
        v-for="item in navigationItems"
        :key="item.routeName || item.title"
        :title="item.title"
        :prepend-icon="item.icon"
        :to="item.routeName ? { name: item.routeName } : undefined"
        :disabled="item.disabled"
        rounded="lg"
      />
    </v-list>
  </v-navigation-drawer>
</template>

<style scoped>
    .sidebar-brand {
        display: flex;
        gap: 12px;
        align-items: center;
        padding: 20px 16px;
    }
</style>