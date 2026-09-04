import { createRouter, createWebHistory } from 'vue-router'

import AuthLayout from '@/layouts/AuthLayout.vue'
import AppLayout from '@/layouts/AppLayout.vue'

import { useAuthStore } from '@/stores/auth'

import InicioView from '@/views/InicioView.vue'
import LoginView from '@/views/LoginView.vue'
import FuncionariosView from '@/views/funcionarios/FuncionariosView.vue'
import FuncionarioFormView from '@/views/funcionarios/FuncionarioFormView.vue'
import FornecedoresView from '@/views/fornecedores/FornecedoresView.vue'
import FornecedorFormView from '@/views/fornecedores/FornecedorFormView.vue'
import ProdutosView from '@/views/produtos/ProdutosView.vue'
import ProdutoFormView from '@/views/produtos/ProdutoFormView.vue'
import ProdutoDetailView from '@/views/produtos/ProdutoDetailView.vue'

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
        {
          path: 'funcionarios',
          name: 'funcionarios',
          component: FuncionariosView,
        },
        {
          path: 'funcionarios/novo',
          name: 'funcionario-create',
          component: FuncionarioFormView,
        },
        {
          path: 'funcionarios/:id/editar',
          name: 'funcionario-edit',
          component: FuncionarioFormView,
        },
        {
          path: 'fornecedores',
          name: 'fornecedores',
          component: FornecedoresView,
        },
        {
          path: 'fornecedores/novo',
          name: 'fornecedor-create',
          component: FornecedorFormView,
        },
        {
          path: 'fornecedores/:id/editar',
          name: 'fornecedor-edit',
          component: FornecedorFormView,
        },
        {
          path: 'produtos',
          name: 'produtos',
          component: ProdutosView,
        },
        {
          path: 'produtos/novo',
          name: 'produto-create',
          component: ProdutoFormView,
        },
        {
          path: 'produtos/:id',
          name: 'produto-detail',
          component: ProdutoDetailView,
        },
        {
          path: 'produtos/:id/editar',
          name: 'produto-edit',
          component: ProdutoFormView,
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
        }
      ],
    },

    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

router.beforeEach(async (to) => {
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

  try {
    await authStore.ensureCurrentUser()
  } catch {
    authStore.logout()

    return {
      name: 'login',
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
