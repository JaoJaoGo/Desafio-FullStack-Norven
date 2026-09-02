<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
    name: 'AppHeader',

    emits: [
        'toggle-navigation',
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

    <v-btn
      icon="mdi-logout"
      variant="text"
      aria-label="Sair"
      @click="$emit('logout')"
    />
  </v-app-bar>
</template>