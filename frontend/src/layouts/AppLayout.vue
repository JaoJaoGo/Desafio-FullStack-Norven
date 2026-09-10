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

    computed: {
        currentUserName(): string {
            const authStore = useAuthStore()

            return authStore.user?.nome ?? 'Usuário'
        },
    },

    methods: {
        toggleNavigation(): void {
            this.drawer = !this.drawer
        },

        async editAccount(): Promise<void> {
            await this.$router.push({
                name: 'account-edit',
            })
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
    :user-name="currentUserName"
    @toggle-navigation="toggleNavigation"
    @edit-account="editAccount"
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