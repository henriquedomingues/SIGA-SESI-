<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '@/services/api'
import { useAuthenticatedUser } from '@/composables/useAuthenticatedUser'
import AlunoLayout from './AlunoLayout.vue'

type NotificationAttachment = {
  idAnexo: number
  nome: string
}

type StudentNotification = {
  id: number
  categoria: string
  prioridade: string
  subject: string
  title: string
  description: string
  date: string
  deadline: string | null
  read: boolean
  entregue: boolean
  atrasada: boolean
  nota: number | null
  comentarioProfessor: string | null
  permitirAtraso: boolean
  anexos: NotificationAttachment[] | null
  expanded: boolean
  _arquivos: File[] | null
  _observacao: string
  _enviando: boolean
}

type NotificationResponse = {
  id: number
  categoria: string
  prioridade: string
  materia: string
  titulo: string
  descricao: string
  data?: string
  dataLimite?: string | null
  lida: boolean
  entregue: boolean
  atrasada: boolean
  nota: number | null
  comentarioProfessor: string | null
  permitirAtraso: boolean
  anexos?: NotificationAttachment[] | null
}

const filterPanel = ref(false)
const notifications = ref<StudentNotification[]>([])
const currentPage = ref(1)
const perPage = 6
const { userId } = useAuthenticatedUser()

const subjectOptions = [
  'Todas as materias',
  'Matematica',
  'Portugues',
  'Historia',
  'Ciencias',
  'Geografia',
  'Educacao Fisica',
  'Artes',
  'Geral',
]

const statusOptions = [
  { title: 'Todos', value: 'all' },
  { title: 'Nao lidas', value: 'unread' },
  { title: 'Lidas', value: 'read' },
]

const limitOptions = [
  { title: 'Todas', value: null },
  { title: 'Ultimas 5', value: 5 },
  { title: 'Ultimas 10', value: 10 },
  { title: 'Ultimas 20', value: 20 },
]

const filters = ref<{
  dateFrom: string | null
  dateTo: string | null
  subject: string
  status: string
  limit: number | null
}>({
  dateFrom: null,
  dateTo: null,
  subject: 'Todas as materias',
  status: 'all',
  limit: null,
})

const unreadCount = computed(() => notifications.value.filter(notification => !notification.read).length)

const totalPages = computed(() =>
  Math.max(1, Math.ceil(notifications.value.length / perPage)),
)

const paginatedNotifications = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return notifications.value.slice(start, start + perPage)
})

function normalizeDate(value?: string | null) {
  return value ? value.split('T')[0]?.split(' ')[0] || '' : ''
}

function mapNotification(notification: NotificationResponse): StudentNotification {
  return {
    id: notification.id,
    categoria: notification.categoria,
    prioridade: notification.prioridade,
    subject: notification.materia || 'Geral',
    title: notification.titulo,
    description: notification.descricao,
    date: normalizeDate(notification.data),
    deadline: normalizeDate(notification.dataLimite) || null,
    read: notification.lida,
    entregue: notification.entregue,
    atrasada: notification.atrasada,
    nota: notification.nota,
    comentarioProfessor: notification.comentarioProfessor,
    permitirAtraso: notification.permitirAtraso,
    anexos: notification.anexos || null,
    expanded: false,
    _arquivos: null,
    _observacao: '',
    _enviando: false,
  }
}

async function fetchNotifications() {
  try {
    const params = new URLSearchParams()
    if (filters.value.status !== 'all') params.append('status', filters.value.status)
    if (filters.value.subject !== 'Todas as materias') params.append('materia', filters.value.subject)
    if (filters.value.dateFrom) params.append('dateFrom', filters.value.dateFrom)
    if (filters.value.dateTo) params.append('dateTo', filters.value.dateTo)
    if (filters.value.limit) params.append('limit', String(filters.value.limit))

    const response = await api.get(`/api/notificacoes/${userId}?${params}`)
    notifications.value = Array.isArray(response.data)
      ? response.data.map((item: NotificationResponse) => mapNotification(item))
      : []
  } catch (error) {
    console.error('Erro ao buscar notificacoes:', error)
  }
}

function applyFilters() {
  currentPage.value = 1
  fetchNotifications()
}

function clearFilters() {
  filters.value = {
    dateFrom: null,
    dateTo: null,
    subject: 'Todas as materias',
    status: 'all',
    limit: null,
  }
  fetchNotifications()
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return ''
  const datePart = String(dateStr).split('T')[0]?.split(' ')[0] || ''
  const [year, month, day] = datePart.split('-')
  return year && month && day ? `${day}/${month}/${year}` : dateStr
}

const subjectColorMap: Record<string, string> = {
  Matematica: 'blue',
  Portugues: 'purple',
  Historia: 'amber',
  Ciencias: 'teal',
  Geografia: 'green',
  'Educacao Fisica': 'orange',
  Artes: 'pink',
}

function subjectColor(subject: string) {
  return subjectColorMap[subject] || 'grey'
}

function toggleNotification(notification: StudentNotification) {
  notification.expanded = !notification.expanded
}

async function markAsRead(id: number) {
  await api.put(`/api/notificacoes/${id}/${userId}/confirmar-leitura`)
  const notification = notifications.value.find(item => item.id === id)
  if (notification) notification.read = true
}

async function markAllRead() {
  await api.put(`/api/notificacoes/todas/${userId}`)
  notifications.value.forEach(notification => {
    notification.read = true
  })
}

async function enviarAtividade(notification: StudentNotification) {
  notification._enviando = true

  const form = new FormData()
  form.append('observacao', notification._observacao || '')

  notification._arquivos?.forEach(file => {
    form.append('arquivos', file)
  })

  try {
    const response = await api.post(`/api/entrega/${notification.id}/${userId}`, form)
    const data = response.data

    if (data.success) {
      notification.entregue = true
      notification.atrasada = data.atrasada
      alert(data.atrasada ? 'Atividade enviada com atraso.' : 'Atividade enviada com sucesso.')
    }
  } catch (error) {
    console.error('Erro ao enviar atividade:', error)
    alert('Nao foi possivel enviar a atividade.')
  } finally {
    notification._enviando = false
  }
}

onMounted(fetchNotifications)
</script>

<template>
  <AlunoLayout
    title="Notificações"
    eyebrow="AREA DO ALUNO"
    description="Acompanhe avisos, atividades, prazos e anexos enviados pelos professores."
    active="notifications"
  >
    <template #app-bar-actions>
      <v-btn
        color="error"
        variant="flat"
        prepend-icon="mdi-filter-variant"
        class="mr-3 text-none"
        rounded="lg"
        @click="filterPanel = !filterPanel"
      >
        <span class="d-none d-sm-inline">Filtrar</span>
      </v-btn>
    </template>

    <template #hero-action>
      <div class="hero-stat">
        <v-icon icon="mdi-bell-ring-outline" size="22" />
        <strong>{{ unreadCount }}</strong>
        <span>nao lidas</span>
      </div>
    </template>

    <v-expand-transition>
      <v-card v-if="filterPanel" flat border rounded="lg" class="mb-5">
        <v-card-title class="px-5 pt-4 pb-2 d-flex align-center">
          <v-icon icon="mdi-filter-variant" color="error" class="mr-2" />
          Filtros de busca
        </v-card-title>
        <v-card-text class="px-5">
          <v-row dense>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="filters.dateFrom"
                label="Data inicial"
                type="date"
                variant="outlined"
                density="comfortable"
                rounded="lg"
                color="error"
                hide-details
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="filters.dateTo"
                label="Data final"
                type="date"
                variant="outlined"
                density="comfortable"
                rounded="lg"
                color="error"
                hide-details
              />
            </v-col>
            <v-col cols="12" sm="6" md="2">
              <v-select
                v-model="filters.subject"
                :items="subjectOptions"
                label="Materia"
                variant="outlined"
                density="comfortable"
                rounded="lg"
                color="error"
                hide-details
              />
            </v-col>
            <v-col cols="12" sm="6" md="2">
              <v-select
                v-model="filters.status"
                :items="statusOptions"
                label="Status"
                variant="outlined"
                density="comfortable"
                rounded="lg"
                color="error"
                hide-details
              />
            </v-col>
            <v-col cols="12" sm="6" md="2">
              <v-select
                v-model="filters.limit"
                :items="limitOptions"
                label="Exibir"
                variant="outlined"
                density="comfortable"
                rounded="lg"
                color="error"
                hide-details
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="px-5 pb-4">
          <v-spacer />
          <v-btn variant="outlined" rounded="lg" class="text-none mr-2" @click="clearFilters">
            Limpar filtros
          </v-btn>
          <v-btn color="error" variant="flat" rounded="lg" class="text-none" @click="applyFilters">
            Aplicar filtros
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-expand-transition>

    <div class="summary-row">
      <div class="summary-info">
        <v-chip
          v-if="unreadCount > 0"
          color="error"
          variant="tonal"
          prepend-icon="mdi-bell-ring"
          size="small"
        >
          {{ unreadCount }} {{ unreadCount === 1 ? 'nao lida' : 'nao lidas' }}
        </v-chip>
        <span class="text-body-2 text-medium-emphasis">
          {{ notifications.length }} notificacoes - pagina {{ currentPage }} de {{ totalPages }}
        </span>
      </div>
      <v-btn
        v-if="unreadCount > 0"
        variant="text"
        size="small"
        color="error"
        class="text-none"
        prepend-icon="mdi-check-all"
        @click="markAllRead"
      >
        Marcar todas como lidas
      </v-btn>
    </div>

    <div v-if="paginatedNotifications.length === 0" class="empty-state">
      <v-icon icon="mdi-bell-off-outline" size="64" color="medium-emphasis" class="mb-4" />
      <p class="text-h6 font-weight-medium text-medium-emphasis">Nenhuma notificação encontrada</p>
      <p class="text-body-2 text-disabled mt-1">Tente ajustar os filtros aplicados</p>
      <v-btn variant="tonal" color="error" class="mt-4 text-none" rounded="lg" @click="clearFilters">
        Limpar filtros
      </v-btn>
    </div>

    <v-row v-else>
      <v-col
        v-for="notification in paginatedNotifications"
        :key="notification.id"
        cols="12"
        sm="6"
        lg="4"
      >
        <v-card
          flat
          :border="`${notification.read ? 'success' : 'error'} md`"
          rounded="lg"
          height="100%"
          class="notification-card d-flex flex-column"
          :class="{ 'unread-card': !notification.read }"
          @click="toggleNotification(notification)"
        >
          <v-card-text class="pa-4 flex-grow-1">
            <div class="card-header">
              <div>
                <v-chip
                  :color="subjectColor(notification.subject)"
                  variant="tonal"
                  size="x-small"
                  class="mb-1 font-weight-bold text-uppercase"
                >
                  {{ notification.subject }}
                </v-chip>
                <p class="text-subtitle-2 font-weight-bold mt-1 mb-0">{{ notification.title }}</p>
              </div>
              <div class="card-status">
                <v-chip :color="notification.read ? 'success' : 'error'" variant="flat" size="x-small">
                  {{ notification.read ? 'Lida' : 'Nova' }}
                </v-chip>
                <v-icon
                  :icon="notification.expanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                  size="18"
                  color="medium-emphasis"
                />
              </div>
            </div>

            <p class="text-body-2 text-medium-emphasis mb-3 notification-description">
              {{ notification.description }}
            </p>

            <div class="d-flex align-center text-caption text-disabled">
              <v-icon icon="mdi-calendar-outline" size="14" class="mr-1" />
              {{ formatDate(notification.date) }}
            </div>

            <v-expand-transition>
              <div v-if="notification.expanded" class="mt-4">
                <v-divider class="mb-3" />

                <div class="mb-3">
                  <v-chip
                    v-if="notification.categoria"
                    color="primary"
                    variant="tonal"
                    size="small"
                    class="mr-2 mb-1"
                  >
                    {{ notification.categoria }}
                  </v-chip>
                  <v-chip
                    v-if="notification.prioridade"
                    color="orange"
                    variant="tonal"
                    size="small"
                    class="mb-1"
                  >
                    {{ notification.prioridade }}
                  </v-chip>
                </div>

                <div v-if="notification.deadline" class="text-body-2 mb-2">
                  <strong>Prazo:</strong> {{ formatDate(notification.deadline) }}
                </div>

                <div v-if="notification.categoria === 'ATIVIDADE'" class="text-body-2 mb-2">
                  <strong>Status:</strong>
                  <span v-if="notification.entregue" class="text-success ml-1">Entregue</span>
                  <span v-else class="text-error ml-1">Nao entregue</span>
                </div>

                <div v-if="notification.atrasada" class="text-body-2 text-warning mb-2">
                  Entregue com atraso
                </div>

                <div v-if="notification.nota !== null && notification.nota !== undefined" class="text-body-2 mb-2">
                  <strong>Nota:</strong> {{ notification.nota }}
                </div>

                <div v-if="notification.comentarioProfessor" class="text-body-2 mb-3">
                  <strong>Comentario:</strong><br>
                  <span class="text-medium-emphasis">{{ notification.comentarioProfessor }}</span>
                </div>

                <v-list v-if="notification.anexos?.length" density="compact" class="mb-2 pa-0">
                  <v-list-item
                    v-for="arquivo in notification.anexos"
                    :key="arquivo.idAnexo"
                    :title="arquivo.nome"
                    density="compact"
                    class="px-0"
                  >
                    <template #prepend>
                      <v-icon icon="mdi-paperclip" size="16" class="mr-1" />
                    </template>
                  </v-list-item>
                </v-list>

                <v-btn
                  v-if="!notification.read"
                  color="success"
                  variant="flat"
                  block
                  rounded="lg"
                  class="mb-2 text-none"
                  prepend-icon="mdi-check"
                  @click.stop="markAsRead(notification.id)"
                >
                  Confirmar leitura
                </v-btn>

                <div v-if="notification.categoria === 'ATIVIDADE' && !notification.entregue">
                  <v-file-input
                    v-model="notification._arquivos"
                    label="Anexar arquivo(s)"
                    multiple
                    prepend-icon="mdi-paperclip"
                    variant="outlined"
                    density="compact"
                    rounded="lg"
                    color="primary"
                    class="mb-2"
                    hide-details
                    @click.stop
                  />

                  <v-textarea
                    v-model="notification._observacao"
                    label="Observacao (opcional)"
                    variant="outlined"
                    density="compact"
                    rounded="lg"
                    rows="2"
                    hide-details
                    class="mb-2"
                    @click.stop
                  />

                  <v-btn
                    color="primary"
                    variant="flat"
                    block
                    rounded="lg"
                    class="text-none"
                    prepend-icon="mdi-upload"
                    :loading="notification._enviando"
                    @click.stop="enviarAtividade(notification)"
                  >
                    Enviar atividade
                  </v-btn>
                </div>
              </div>
            </v-expand-transition>
          </v-card-text>

          <div v-if="notification.read && !notification.expanded" class="pb-3" />
        </v-card>
      </v-col>
    </v-row>

    <div v-if="totalPages > 1" class="pagination-row">
      <v-pagination
        v-model="currentPage"
        :length="totalPages"
        :total-visible="7"
        active-color="error"
        rounded="lg"
        density="comfortable"
      />
      <span class="text-body-2 text-medium-emphasis ml-2">
        Mostrando {{ paginatedNotifications.length }} de {{ notifications.length }}
      </span>
    </div>
  </AlunoLayout>
</template>

<style scoped>
.hero-stat {
  min-width: 142px;
  padding: 16px 18px;
  color: white;
  background: #222222;
}

.hero-stat strong,
.hero-stat span {
  display: block;
}

.hero-stat strong {
  margin-top: 8px;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 32px;
  line-height: 1;
}

.hero-stat span {
  margin-top: 5px;
  color: #c9c5c1;
  font-size: 12px;
}

.summary-row,
.summary-info,
.card-header,
.card-status,
.pagination-row {
  display: flex;
  align-items: center;
}

.summary-row {
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.summary-info {
  gap: 12px;
  flex-wrap: wrap;
}

.empty-state {
  min-height: 360px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 16px;
  text-align: center;
}

.notification-card {
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.notification-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
}

.unread-card {
  background: rgba(196, 30, 42, 0.02);
}

.card-header {
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.card-status {
  gap: 4px;
  margin-left: 8px;
  flex-shrink: 0;
}

.notification-description {
  line-height: 1.55;
}

.pagination-row {
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 24px;
}

@media (max-width: 700px) {
  .hero-stat {
    min-width: 0;
  }
}
</style>
