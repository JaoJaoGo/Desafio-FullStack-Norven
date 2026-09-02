<script lang="ts">
import { defineComponent } from 'vue'
import { ApiError } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

export default defineComponent({
    name: 'LoginView',

    data() {
        return {
            email: '',
            password: '',
            showPassword: false,
            loading: false,
            errorMessage: '',
        }
    },

    methods: {
        async submitLogin(): Promise<void> {
            this.errorMessage = ''

            if (!this.email.trim()) {
                this.errorMessage = 'Informe seu e-mail.'

                return
            }

            if (!this.password) {
                this.errorMessage = "Informe sua senha."

                return
            }

            this.loading = true

            try {
                const authStore = useAuthStore()

                await authStore.login({
                    email: this.email.trim(),
                    password: this.password,
                })

                const redirect = typeof this.$route.query.redirect === 'string' ? this.$route.query.redirect : '/'

                await this.$router.replace(redirect)
            } catch (error: unknown) {
                if (error instanceof ApiError) {
                    this.errorMessage = error.message
                } else {
                    this.errorMessage = "Não foi possível realizar o login."
                }
            } finally {
                this.loading = false
            }
        },
    },
})
</script>

<template>
  <v-main class="login-page">
    <v-container
      class="login-container"
      fluid
    >
      <v-row
        align="center"
        justify="center"
        class="login-row"
      >
        <v-col
          cols="12"
          sm="9"
          md="6"
          lg="4"
          xl="3"
        >
          <v-card
            class="login-card"
            elevation="10"
            rounded="xl"
          >
            <v-card-text class="pa-8">
              <div class="login-heading">
                <v-avatar
                  size="64"
                  class="mb-5"
                >
                  <v-icon
                    icon="mdi-package-variant-closed"
                    size="36"
                  />
                </v-avatar>
                <h1 class="text-h4 font-weight-bold">
                  Norven
                </h1>
                <p class="text-body-1 text-medium-emphasis mt-2">
                  Gerenciamento de estoque
                </p>
              </div>

              <v-alert
                v-if="errorMessage"
                type="error"
                variant="tonal"
                class="mt-6"
                closable
                @click:close="errorMessage = ''"
              >
                {{ errorMessage }}
              </v-alert>
              <v-form
                class="mt-7"
                @submit.prevent="submitLogin"
              >
                <v-text-field
                  v-model="email"
                  label="E-mail"
                  type="email"
                  variant="outlined"
                  prepend-inner-icon="mdi-email-outline"
                  autocomplete="username"
                  :disabled="loading"
                  required
                />
                <v-text-field
                  v-model="password"
                  label="Senha"
                  :type="showPassword ? 'text' : 'password'"
                  variant="outlined"
                  prepend-inner-icon="mdi-lock-outline"
                  :append-inner-icon="showPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
                  autocomplete="current-password"
                  :disabled="loading"
                  required
                  @click:append-inner="showPassword = !showPassword"
                />
                                
                <v-btn
                  type="submit"
                  block
                  size="large"
                  class="mt-2"
                  :loading="loading"
                  :disabled="loading"
                >
                  Entrar
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<style scoped>
.login-page {
    min-height: 100vh;
    background: linear-gradient(135deg, rgb(var(--v-theme-surface)) 0%, rgb(var(--v-theme-surface-variant)) 100%);
}

.login-container,
.login-row {
    min-height: 100vh;
}

.login-card {
    width: 100%;
}

.login-heading {
    text-align: center;
}
</style>