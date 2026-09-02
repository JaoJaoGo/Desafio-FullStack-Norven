import { createRouter, createWebHistory } from 'vue-router'

import AuthLayout from '@/layouts/AuthLayout.vue'
import AppLayout from '@/layouts/AppLayout.vue'

import { useAuthStore } from '@/stores/auth'

import InicioView from '@/views/InicioView.vue'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      meta: {
        requiresAuth: true,
      },

      children: [
        {
          path: '',
          name: 'inicio',
          component: InicioView,
        },
      ],
    },

    {
      path: '/login',
      component: AuthLayout,
      
      children: [
        {
          path: '',
          name: 'login',
          component: LoginView,
          meta: {
            guestOnly: true,
          },
        },
      ],
    },

    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  const requiresAuth = to.matched.some((route) => route.meta.requiresAuth)
  const guestOnly = to.matched.some((route) => route.meta.guestOnly)

  if (requiresAuth && !authStore.isAuthenticated) {
    return {
      name: 'login',

      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (guestOnly && authStore.isAuthenticated) {
    return {
      name: 'inicio',
    }
  }

  return true
})

export default router
