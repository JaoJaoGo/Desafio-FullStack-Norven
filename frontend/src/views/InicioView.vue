<script lang="ts">
import { defineComponent } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default defineComponent({
    name: 'InicioView',

    methods: {
        async logout(): Promise<void> {
            const authStore = useAuthStore()

            authStore.logout()

            await this.$router.replace({name: 'login'})
        },
    },
})
</script>

<template>
  <v-main>
    <v-container class="py-10">
      <v-row justify="center">
        <v-col
          cols="12"
          md="8"
          lg="6"
        >
          <v-card
            rounded="xl"
            elevation="4"
          >
            <v-card-text class="pa-8">
              <div class="d-flex align-center justify-space-between">
                <div>
                  <h1 class="text-h4 font-weight-bold">
                    Sistema Norven
                  </h1>
                  <p class="text-body-1 text-medium-emphasis mt-2">
                    Autenticação realizada com sucesso.
                  </p>
                </div>

                <v-btn
                  variant="outlined"
                  prepend-icon="mdi-logout"
                  @click="logout"
                >
                  Sair
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>