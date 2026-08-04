import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { jwtDecode } from 'jwt-decode'

type UserRole = 'ALUNO' | 'PROFESSOR'

type TokenPayload = {
  exp?: number
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/aluno',
    component: () => import('../views/viewsAlunos/NotificacoesView.vue'),
    meta: { requiresAuth: true, role: 'ALUNO' }
  },
  {
    path: '/professor',
    component: () => import('../views/ProfessorView.vue'),
    meta: { requiresAuth: true, role: 'PROFESSOR' }
  },
  {
    path: '/centraldecomando',
    component: () => import('../views/viewsProfessores/CentralDeComando.vue'),
    meta: { requiresAuth: true, role: 'PROFESSOR' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const tipoUser = localStorage.getItem('tipoUser') as UserRole | null

  if (to.meta.requiresAuth) {
    if (!token) return next('/')

    try {
      const decoded = jwtDecode<TokenPayload>(token)
      const now = Math.floor(Date.now() / 1000)

      if (decoded.exp && decoded.exp < now) {
        localStorage.removeItem('token')
        localStorage.removeItem('tipoUser')
        return next('/')
      }

      if (to.meta.role && to.meta.role !== tipoUser) {
        return next('/')
      }
    } catch (err) {
      localStorage.removeItem('token')
      localStorage.removeItem('tipoUser')
      return next('/')
    }
  }

  next()
})

export default router
