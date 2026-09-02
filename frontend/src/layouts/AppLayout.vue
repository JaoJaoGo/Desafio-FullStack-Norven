<script lang="ts">
import { defineComponent } from 'vue'

import AppHeader from '@/components/AppHeader.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import { useAuthStore } from '@/stores/auth'

export default defineComponent({
    name: 'AppLayout',

    components: {
        AppHeader,
        AppSidebar,
    },

    data() {
        return {
            drawer: true,
        }
    },

    methods: {
        toggleNavigation(): void {
            this.drawer = !this.drawer
        },

        async logout(): Promise<void> {
            const authStore = useAuthStore()

            authStore.logout()

            await this.$router.replace({
                name: 'login',
            })
        },
    },
})
</script>

<template>
  <app-sidebar v-model="drawer" />

  <app-header
    @toggle-navigation="toggleNavigation"
    @logout="logout"
  />

  <v-main class="app-content">
    <router-view />
  </v-main>
</template>

<style scoped>
.app-content {
    min-height: 100vh;
    background: rgb(var(--v-theme-background));
}
</style>