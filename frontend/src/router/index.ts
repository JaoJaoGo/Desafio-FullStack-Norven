import { createRouter, createWebHistory } from 'vue-router'

import AuthLayout from '@/layouts/AuthLayout.vue'
import AppLayout from '@/layouts/AppLayout.vue'

import { useAuthStore } from '@/stores/auth'

const InicioView = () => import('@/views/InicioView.vue')
const LoginView = () => import('@/views/LoginView.vue')
const FuncionariosView = () => import('@/views/funcionarios/FuncionariosView.vue')
const FuncionarioDetailView = () => import('@/views/funcionarios/FuncionarioDetailView.vue')
const FuncionarioFormView = () => import('@/views/funcionarios/FuncionarioFormView.vue')
const FornecedoresView = () => import('@/views/fornecedores/FornecedoresView.vue')
const FornecedorDetailView = () => import('@/views/fornecedores/FornecedorDetailView.vue')
const FornecedorFormView = () => import('@/views/fornecedores/FornecedorFormView.vue')
const ProdutosView = () => import('@/views/produtos/ProdutosView.vue')
const ProdutoFormView = () => import('@/views/produtos/ProdutoFormView.vue')
const ProdutoDetailView = () => import('@/views/produtos/ProdutoDetailView.vue')
const TransacoesView = () => import('@/views/transacoes/TransacoesView.vue')

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
          path: 'funcionarios/:id',
          name: 'funcionario-detail',
          component: FuncionarioDetailView
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
          path: 'fornecedores/:id',
          name: 'fornecedor-detail',
          component: FornecedorDetailView,
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
        {
          path: 'transacoes',
          name: 'transacoes',
          component: TransacoesView,
        }
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
