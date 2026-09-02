<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
    name: 'AuthLayout'
})
</script>

<template>
  <v-main class="auth-layout">
    <v-container
      fluid
      class="auth-container"
    >
      <v-row
        align="center"
        justify="center"
        class="auth-row"
      >
        <v-col
          cols="12"
          sm="9"
          md="6"
          lg="4"
          xl="3"
        >
          <router-view />
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<style scoped>
.auth-layout {
    min-height: 100vh;
    background: linear-gradient(135deg, rgb(var(--v-theme-surface)) 0%, rgb(var(--v-theme-surface-variant)) 100%);
}

.auth-container,
.auth-row {
    min-height: 100vh;
}
</style>