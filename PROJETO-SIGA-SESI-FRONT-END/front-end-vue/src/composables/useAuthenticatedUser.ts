import { computed, ref } from 'vue'
import { jwtDecode } from 'jwt-decode'
import api from '@/services/api'

type CurrentUser = {
  name: string
  turma: string
}

export function useAuthenticatedUser() {
  const currentUser = ref<CurrentUser>({ name: '', turma: '' })
  const token = localStorage.getItem('token')
  const decoded: any = token ? jwtDecode(token) : {}
  const userId = Number(decoded.sub || 0)

  const userInitials = computed(() => {
    if (!currentUser.value.name) return 'U'
    return currentUser.value.name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map(name => name[0])
      .join('')
      .toUpperCase()
  })

  async function fetchUser() {
    if (!userId) return

    try {
      const response = await api.get(`/api/usuario/${userId}`)
      const data = response.data
      currentUser.value = { name: data.nome || 'Usuario', turma: data.turma || '' }
    } catch (error) {
      console.error('Erro ao buscar usuario:', error)
    }
  }

  return {
    currentUser,
    userId,
    userInitials,
    fetchUser,
  }
}
