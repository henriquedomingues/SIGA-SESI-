import { createRouter, createWebHistory } from 'vue-router'
import { jwtDecode } from "jwt-decode";

const routes = [
  {
    path: '/',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/aluno',
    component: () => import('../views/AlunoView.vue'),
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
  },
  {
    
    path: '/criar-notificacao',
    name: 'criar-notificacao',
    component: () => import('../views/CriarNotificacaoView.vue'),
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token")
  const tipoUser = localStorage.getItem("tipoUser")

  if (to.meta.requiresAuth) {
    if (!token) return next('/')

    try {
      const decoded: any = jwtDecode(token)
      const now = Math.floor(Date.now() / 1000)

      if (decoded.exp && decoded.exp < now) {
        localStorage.removeItem("token")
        localStorage.removeItem("tipoUser")
        return next('/')
      }

      if (to.meta.role && to.meta.role !== tipoUser) {
        return next('/')
      }
    } catch (err) {
      localStorage.removeItem("token")
      localStorage.removeItem("tipoUser")
      return next('/')
    }
  }

  next()
})

export default router
