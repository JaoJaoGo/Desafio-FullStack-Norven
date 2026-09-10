<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
    name: 'AppHeader',

    props: {
      userName: {
        type: String,
        required: true,
      }
    },

    emits: [
        'toggle-navigation',
        'edit-account',
        'logout',
    ],
})
</script>

<template>
  <v-app-bar
    elevation="1"
    border="b"
  >
    <v-app-bar-nav-icon
      aria-label="Alternar menu lateral"
      @click="$emit('toggle-navigation')"
    />

    <v-app-bar-title>Gerenciamento de Estoque</v-app-bar-title>

    <v-spacer />

    <v-menu>
      <template #activator="{ props }">
        <v-btn
          v-bind="props"
          variant="text"
          append-icon="mdi-chevron-down"
          class="text-none"
        >
          Olá, {{ userName }}
        </v-btn>
      </template>

      <v-list
        nav
        density="comfortable"
      >
        <v-list-item
          title="Editar conta"
          prepend-icon="mdi-account-edit-outline"
          @click="$emit('edit-account')"
        />

        <v-divider class="my-1" />

        <v-list-item
          title="Sair"
          prepend-icon="mdi-logout"
          @click="$emit('logout')"
        />
      </v-list>
    </v-menu>
  </v-app-bar>
</template>