<script setup>
import { ref, computed, onMounted } from 'vue'

// ─────────────────────────
// UI STATE
// ─────────────────────────
const theme = ref('light')
function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}
const drawer = ref(true)
const rail = ref(false)
const mobileDrawer = ref(false)
const filterPanel = ref(false)

// ─────────────────────────
// USER
// ─────────────────────────
const currentUser = ref({ name: '', turma: '' })
const userInitials = computed(() => {
  if (!currentUser.value.name) return 'U'
  return currentUser.value.name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map(n => n[0])
    .join('')
    .toUpperCase()
})

// ─────────────────────────
// NAVIGATION
// ─────────────────────────
const navItems = ref([
  { title: 'Início', icon: 'mdi-view-dashboard-outline', active: false },
  { title: 'Notificações', icon: 'mdi-bell-outline', active: true },
])
function navigate(item) {
  navItems.value.forEach(n => (n.active = false))
  item.active = true
}

// ─────────────────────────
// FILTERS
// ─────────────────────────
const subjectOptions = [
  'Todas as matérias', 'Matemática', 'Português', 'História',
  'Ciências', 'Geografia', 'Educação Física', 'Artes', 'Geral'
]
const statusOptions = [
  { title: 'Todos', value: 'all' },
  { title: 'Não lidas', value: 'unread' },
  { title: 'Lidas', value: 'read' },
]
const limitOptions = [
  { title: 'Todas', value: null },
  { title: 'Últimas 5', value: 5 },
  { title: 'Últimas 10', value: 10 },
  { title: 'Últimas 20', value: 20 },
]
const filters = ref({
  dateFrom: null,
  dateTo: null,
  subject: 'Todas as matérias',
  status: 'all',
  limit: null,
})

// ─────────────────────────
// DATA
// ─────────────────────────
const notifications = ref([])
const userId = 1



// ─────────────────────────
// FETCH BACKEND
// ─────────────────────────
async function fetchNotifications() {
  try {
    const params = new URLSearchParams()
    if (filters.value.status !== 'all') params.append('status', filters.value.status)
    if (filters.value.subject !== 'Todas as matérias') params.append('materia', filters.value.subject)
    if (filters.value.dateFrom) params.append('dateFrom', filters.value.dateFrom)
    if (filters.value.dateTo) params.append('dateTo', filters.value.dateTo)
    if (filters.value.limit) params.append('limit', filters.value.limit)

    const response = await fetch(`http://localhost:8000/api/notificacoes/${userId}?${params}`)
    const data = await response.json()

    notifications.value = Array.isArray(data)
      ? data.map(n => ({
          id: n.id,

          categoria: n.categoria,
          prioridade: n.prioridade,

          subject: n.materia,

          title: n.titulo,
          description: n.descricao,

          date: n.data ? n.data.split('T')[0].split(' ')[0] : '',
          deadline: n.dataLimite ? n.dataLimite.split('T')[0].split(' ')[0] : null,

          read: n.lida,

          entregue: n.entregue,
          atrasada: n.atrasada,

          nota: n.nota,

          comentarioProfessor: n.comentarioProfessor,

          permitirAtraso: n.permitirAtraso,

          anexos: n.anexos || null,

          expanded: false,

          _arquivos: null,
          _observacao: '',
          _enviando: false,
        }))
      : []
  } catch (error) {
    console.error('Erro ao buscar notificações:', error)
  }
}

async function fetchUser() {
  try {
    const response = await fetch(`http://localhost:8000/api/usuario/${userId}`)
    const data = await response.json()
    currentUser.value = { name: data.nome || 'Usuário', turma: data.turma || '' }
  } catch (error) {
    console.error('Erro ao buscar usuário:', error)
  }
}

// ─────────────────────────
// FILTER ACTIONS
// ─────────────────────────
function applyFilters() {
  currentPage.value = 1
  fetchNotifications()
}
function clearFilters() {
  filters.value = { dateFrom: null, dateTo: null, subject: 'Todas as matérias', status: 'all', limit: null }
  fetchNotifications()
}

// ─────────────────────────
// PAGINATION
// ─────────────────────────
const currentPage = ref(1)
const PER_PAGE = 6
const totalPages = computed(() =>
  Math.max(1, Math.ceil(notifications.value.length / PER_PAGE))
)
const paginatedNotifications = computed(() => {
  const start = (currentPage.value - 1) * PER_PAGE
  return notifications.value.slice(start, start + PER_PAGE)
})

// ─────────────────────────
// HELPERS
// ─────────────────────────
const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

function formatDate(dateStr) {
  if (!dateStr) return ''
  // Suporta "2026-04-27T15:35:27", "2026-04-27 15:35:27" e "2026-04-27"
  const datePart = String(dateStr).split('T')[0].split(' ')[0]
  const parts = datePart.split('-')
  if (parts.length !== 3) return dateStr
  const [y, m, d] = parts
  return `${d}/${m}/${y}`
}

const subjectColorMap = {
  'Matemática': 'blue',
  'Português': 'purple',
  'História': 'amber',
  'Ciências': 'teal',
  'Geografia': 'green',
  'Educação Física': 'orange',
  'Artes': 'pink',
}
function subjectColor(subject) {
  return subjectColorMap[subject] || 'grey'
}

// ─────────────────────────
// TOGGLE EXPAND
// ─────────────────────────
function toggleNotification(notif) {
  notif.expanded = !notif.expanded
}

// ─────────────────────────
// ACTIONS
// ─────────────────────────
async function markAsRead(id) {
  await fetch(`http://localhost:8000/api/notificacoes/${id}/${userId}/confirmar-leitura`, { method: 'PUT' })
  const notif = notifications.value.find(n => n.id === id)
  if (notif) notif.read = true
}

async function markAllRead() {
  await fetch(`http://localhost:8000/api/notificacoes/todas/${userId}`, { method: 'PUT' })
  notifications.value.forEach(n => n.read = true)
}

async function enviarAtividade(notif) {
  notif._enviando = true

  const form = new FormData()

  form.append(
    'observacao',
    notif._observacao || ''
  )

  if (notif._arquivos) {
    for (const arquivo of notif._arquivos) {
      form.append('arquivos', arquivo)
    }
  }

  try {
    const res = await fetch(
      `http://localhost:8000/api/entrega/${notif.id}/${userId}`,
      {
        method: 'POST',
        body: form
      }
    )

    const data = await res.json()

    if (data.success) {
      notif.entregue = true
      notif.atrasada = data.atrasada
    }

  

  } catch (err) {
    alert(
    data.atrasada
      ? 'Atividade enviada com atraso.'
      : 'Atividade enviada com sucesso.'
  )
  } finally {
    notif._enviando = false
  }
}

// ─────────────────────────
// INIT
// ─────────────────────────
onMounted(() => {
  fetchNotifications()
  fetchUser()
})
</script>

<template>
  <v-app :theme="theme">

    <!-- ===== NAVIGATION DRAWER (Desktop) ===== -->
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      permanent
      :class="['sidebar-drawer', theme === 'dark' ? 'sidebar-dark' : 'sidebar-light']"
    >
      <v-list-item nav class="py-4 px-3">
        <template #prepend>
          <div class="sesi-logo-badge">SIGA SESI</div>
        </template>
      </v-list-item>

      <v-divider />

      <v-list density="compact" nav class="mt-2">
        <v-list-item
          v-for="item in navItems"
          :key="item.title"
          :prepend-icon="item.icon"
          :title="item.title"
          :value="item.title"
          :active="item.active"
          active-color="error"
          rounded="lg"
          class="mb-1"
          @click="navigate(item)"
        >
          <template v-if="item.badge" #append>
            <v-badge :content="item.badge" color="error" inline />
          </template>
        </v-list-item>
      </v-list>

      <template #append>
        <v-divider />
        <v-list-item :title="currentUser.name" :subtitle="currentUser.turma" nav class="py-3">
          <template #prepend>
            <v-avatar color="error" size="34">
              <span class="text-caption font-weight-bold text-white">{{ userInitials }}</span>
            </v-avatar>
          </template>
          <template #append>
            <v-btn
              :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"
              variant="text"
              size="small"
              @click="rail = !rail"
            />
          </template>
        </v-list-item>
      </template>
    </v-navigation-drawer>

    <!-- ===== APP BAR ===== -->
    <v-app-bar flat :border="'b'" :class="theme === 'dark' ? 'bg-surface' : 'bg-white'">
      <v-app-bar-nav-icon class="d-flex d-md-none" @click="mobileDrawer = true" />
      <v-app-bar-title>
        <span class="text-h6 font-weight-bold">Notificações</span>
      </v-app-bar-title>
      <template #append>
        <v-btn
          :icon="theme === 'dark' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
          variant="text"
          class="mr-1"
          @click="toggleTheme"
        />
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
    </v-app-bar>

    <!-- ===== MOBILE DRAWER ===== -->
    <v-navigation-drawer
      v-model="mobileDrawer"
      temporary
      :class="theme === 'dark' ? 'sidebar-dark' : 'sidebar-light'"
    >
      <v-list-item class="py-4 px-3">
        <template #prepend>
          <div class="sesi-logo-badge">SESI</div>
        </template>
        <template #title>
          <span class="sidebar-app-title">Portal do Aluno</span>
        </template>
      </v-list-item>
      <v-divider />
      <v-list density="compact" nav class="mt-2">
        <v-list-item
          v-for="item in navItems"
          :key="item.title"
          :prepend-icon="item.icon"
          :title="item.title"
          :value="item.title"
          :active="item.active"
          active-color="error"
          rounded="lg"
          class="mb-1"
        >
          <template v-if="item.badge" #append>
            <v-badge :content="item.badge" color="error" inline />
          </template>
        </v-list-item>
      </v-list>
      <template #append>
        <v-divider />
        <v-list-item :title="currentUser.name" :subtitle="currentUser.turma" nav class="py-3">
          <template #prepend>
            <v-avatar color="error" size="34">
              <span class="text-caption font-weight-bold text-white">{{ userInitials }}</span>
            </v-avatar>
          </template>
        </v-list-item>
      </template>
    </v-navigation-drawer>

    <!-- ===== MAIN CONTENT ===== -->
    <v-main>
      <v-container fluid class="pa-4 pa-md-6">

        <!-- ===== FILTER PANEL ===== -->
        <v-expand-transition>
          <v-card v-if="filterPanel" flat border rounded="xl" class="mb-5">
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
                    label="Matéria"
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

        <!-- ===== SUMMARY ROW ===== -->
        <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
          <div class="d-flex align-center gap-3">
            <v-chip
              v-if="unreadCount > 0"
              color="error"
              variant="tonal"
              prepend-icon="mdi-bell-ring"
              size="small"
            >
              {{ unreadCount }} não {{ unreadCount === 1 ? 'lida' : 'lidas' }}
            </v-chip>
            <span class="text-body-2 text-medium-emphasis">
              {{ notifications.length }} notificações — página {{ currentPage }} de {{ totalPages }}
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

        <!-- ===== EMPTY STATE ===== -->
        <div
          v-if="paginatedNotifications.length === 0"
          class="d-flex flex-column align-center justify-center py-16"
        >
          <v-icon icon="mdi-bell-off-outline" size="64" color="medium-emphasis" class="mb-4" />
          <p class="text-h6 font-weight-medium text-medium-emphasis">Nenhuma notificação encontrada</p>
          <p class="text-body-2 text-disabled mt-1">Tente ajustar os filtros aplicados</p>
          <v-btn variant="tonal" color="error" class="mt-4 text-none" rounded="lg" @click="clearFilters">
            Limpar filtros
          </v-btn>
        </div>

        <!-- ===== NOTIFICATIONS GRID ===== -->
        <v-row v-else>
          <v-col
            v-for="notif in paginatedNotifications"
            :key="notif.id"
            cols="12"
            sm="6"
            lg="4"
          >
            <v-card
              flat
              :border="`${notif.read ? 'success' : 'error'} md`"
              rounded="xl"
              height="100%"
              class="notification-card d-flex flex-column"
              :class="{ 'unread-card': !notif.read }"
              style="cursor: pointer"
              @click="toggleNotification(notif)"
            >
              <v-card-text class="pa-4 flex-grow-1">

                <!-- Header row -->
                <div class="d-flex align-start justify-space-between mb-2">
                  <div>
                    <v-chip
                      :color="subjectColor(notif.subject)"
                      variant="tonal"
                      size="x-small"
                      class="mb-1 font-weight-bold text-uppercase"
                    >
                      {{ notif.subject }}
                    </v-chip>
                    <p class="text-subtitle-2 font-weight-bold mt-1 mb-0">{{ notif.title }}</p>
                  </div>
                  <div class="d-flex align-center gap-1 ml-2 flex-shrink-0">
                    <v-chip :color="notif.read ? 'success' : 'error'" variant="flat" size="x-small">
                      {{ notif.read ? 'Lida' : 'Nova' }}
                    </v-chip>
                    <v-icon
                      :icon="notif.expanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                      size="18"
                      color="medium-emphasis"
                    />
                  </div>
                </div>

                <!-- Description -->
                <p class="text-body-2 text-medium-emphasis mb-3" style="line-height:1.55">
                  {{ notif.description }}
                </p>

                <!-- Date row -->
                <div class="d-flex align-center text-caption text-disabled">
                  <v-icon icon="mdi-calendar-outline" size="14" class="mr-1" />
                  {{ formatDate(notif.date) }}
                </div>

                <!-- ===== EXPANDED DETAILS ===== -->
                <v-expand-transition>
                  <div v-if="notif.expanded" class="mt-4">

                    <v-divider class="mb-3" />

                    <!-- Categoria + Prioridade -->
                    <div class="mb-3">
                      <v-chip
                        v-if="notif.categoria"
                        color="primary"
                        variant="tonal"
                        size="small"
                        class="mr-2 mb-1"
                      >
                        {{ notif.categoria }}
                      </v-chip>
                      <v-chip
                        v-if="notif.prioridade"
                        color="orange"
                        variant="tonal"
                        size="small"
                        class="mb-1"
                      >
                        {{ notif.prioridade }}
                      </v-chip>
                    </div>

                    <!-- Prazo -->
                    <div v-if="notif.deadline" class="text-body-2 mb-2">
                      <strong>Prazo:</strong> {{ formatDate(notif.deadline) }}
                    </div>

                    <!-- Status da entrega -->
                    <div v-if="notif.categoria === 'ATIVIDADE'" class="text-body-2 mb-2">
                      <strong>Status:</strong>
                      <span v-if="notif.entregue" class="text-success ml-1">✅ Entregue</span>
                      <span v-else class="text-error ml-1">❌ Não entregue</span>
                    </div>

                    <!-- Entrega atrasada -->
                    <div v-if="notif.atrasada" class="text-body-2 text-warning mb-2">
                      ⏰ Entregue com atraso
                    </div>

                    <!-- Nota -->
                    <div v-if="notif.nota !== null && notif.nota !== undefined" class="text-body-2 mb-2">
                      <strong>Nota:</strong> {{ notif.nota }}
                    </div>

                    <!-- Comentário do professor -->
                    <div v-if="notif.comentarioProfessor" class="text-body-2 mb-3">
                      <strong>Comentário:</strong><br />
                      <span class="text-medium-emphasis">{{ notif.comentarioProfessor }}</span>
                    </div>

                    <!-- Anexos do professor -->
                    <v-list v-if="notif.anexos && notif.anexos.length" density="compact" class="mb-2 pa-0">
                      <v-list-item
                        v-for="arquivo in notif.anexos"
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

                    
                      <div>
                        Categoria: {{ notif.categoria }}
                      </div>                    
                    <!-- Botão confirmar leitura -->
                    <v-btn
                      v-if="!notif.read"
                      color="success"
                      variant="flat"
                      block
                      rounded="lg"
                      class="mb-2 text-none"
                      prepend-icon="mdi-check"
                      @click.stop="markAsRead(notif.id)"
                    >
                      Confirmar leitura
                    </v-btn>
                    
                    

                    <!-- Botão enviar atividade -->
                    <div v-if="notif.categoria === 'ATIVIDADE' && !notif.entregue">
                      <v-file-input
                        v-model="notif._arquivos"
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
                        v-model="notif._observacao"
                        label="Observação (opcional)"
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
                        :loading="notif._enviando"
                        @click.stop="enviarAtividade(notif)"
                      >
                        Enviar atividade
                      </v-btn>



                    </div>

                  </div>
                </v-expand-transition>

              </v-card-text>

              <!-- Fallback bottom padding when read and not expanded -->
              <div v-if="notif.read && !notif.expanded" class="pb-3" />

            </v-card>
          </v-col>
        </v-row>

        <!-- ===== PAGINATION ===== -->
        <div
          v-if="totalPages > 1"
          class="d-flex align-center justify-center mt-6 flex-wrap gap-2"
        >
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

      </v-container>
    </v-main>

  </v-app>
</template>

<style scoped>
.sesi-logo-badge {
  background: #C41E2A;
  color: #fff;
  font-weight: 800;
  font-size: 16px;
  letter-spacing: 1.5px;
  padding: 4px 10px;
  border-radius: 4px;
  line-height: 1;
  flex-shrink: 0;
}

.sidebar-app-title {
  font-size: 13px;
  font-weight: 600;
}

.sidebar-light { background: #fff !important; }
.sidebar-dark  { background: #1c1c1e !important; }

.notification-card {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.notification-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
}
.unread-card {
  background: rgba(196, 30, 42, 0.02);
}

@media (max-width: 959px) {
  .v-navigation-drawer--permanent {
    display: none !important;
  }
}
</style>