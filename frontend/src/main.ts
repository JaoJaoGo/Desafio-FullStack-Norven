import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'

import { configureApiAuth } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)

const authStore = useAuthStore(pinia)

configureApiAuth({
    getAccessToken: () => authStore.token,
    onUnauthorized: () => authStore.logout()
})

app.use(router)
app.use(vuetify)

app.mount('#app')
