<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

type Option = {
  id: number
  nome: string
}

type ClassOption = Option & {
  anoLetivo: number
  idEscola: number | null
  totalAlunos: number
}

type StudentOption = Option & {
  idClasseDeAula: number | null
  turma: string | null
}

type NotificationConfig = {
  categorias: string[]
  prioridades: string[]
  classes: ClassOption[]
  materias: Option[]
  alunos: StudentOption[]
  professores: Option[]
}

type CreatedNotification = {
  id: number
  titulo: string
  descricao: string
  dataMensagem: string
  materia: string | null
  professor: string | null
  categoria: string
  prioridade: string
  agendada: boolean
  dataAgendamento: string | null
  publicada: boolean
  ativa: boolean
  totalDestinatarios: number
  totalTurmas: number
  totalAnexos: number
}

const emptyConfig: NotificationConfig = {
  categorias: ['AVISO', 'ATIVIDADE'],
  prioridades: ['BAIXA', 'NORMAL', 'ALTA', 'URGENTE'],
  classes: [],
  materias: [],
  alunos: [],
  professores: [],
}

const createInitialForm = () => ({
  titulo: '',
  descricao: '',
  categoria: 'AVISO',
  prioridade: 'NORMAL',
  idMateria: null as number | null,
  idProfessor: null as number | null,
  classes: [] as number[],
  alunos: [] as number[],
  solicitarConfirmacaoLeitura: false,
  modoPublicacao: 'AGORA',
  dataAgendamento: '',
  dataLimite: '',
  permitirAtraso: false,
  ativa: true,
})

const theme = ref('light')
const router = useRouter()
const drawer = ref(true)
const rail = ref(false)
const mobileDrawer = ref(false)
const activePanel = ref('create')
const currentUser = ref({ name: '', turma: '' })
const userId = 1

const navItems = [
  { title: 'Criar notificações', value: 'create', icon: 'mdi-bell-plus-outline' },
  { title: 'Central de Controle', value: 'central', icon: 'mdi-view-dashboard-outline' },
]

const config = ref<NotificationConfig>(emptyConfig)
const form = ref(createInitialForm())
const files = ref<File[]>([])
const recentNotifications = ref<CreatedNotification[]>([])
const loading = ref(true)
const submitting = ref(false)
const showRecent = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const appBarTitle = computed(() =>
  activePanel.value === 'create' ? 'Criar notificações' : 'Notificações',
)

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

const isActivity = computed(() => form.value.categoria === 'ATIVIDADE')
const selectedClasses = computed(() =>
  config.value.classes.filter(item => form.value.classes.includes(item.id)),
)
const selectedStudents = computed(() =>
  config.value.alunos.filter(item => form.value.alunos.includes(item.id)),
)
const estimatedRecipients = computed(() => {
  const classStudentIds = new Set(
    config.value.alunos
      .filter(student =>
        student.idClasseDeAula !== null &&
        form.value.classes.includes(student.idClasseDeAula),
      )
      .map(student => student.id),
  )
  form.value.alunos.forEach(id => classStudentIds.add(id))
  return classStudentIds.size
})
const selectedSubject = computed(() =>
  config.value.materias.find(item => item.id === form.value.idMateria)?.nome || 'Geral',
)
const publicationLabel = computed(() => {
  if (form.value.modoPublicacao === 'AGENDAR') return 'Agendada'
  if (form.value.modoPublicacao === 'RASCUNHO') return 'Rascunho'
  return 'Publicada agora'
})
const priorityColor = computed(() => {
  const colors: Record<string, string> = {
    BAIXA: '#56806c',
    NORMAL: '#3d6ea8',
    ALTA: '#d17a22',
    URGENTE: '#c7192d',
  }
  return colors[form.value.prioridade] || colors.NORMAL
})

function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

function navigate(value: string) {
  mobileDrawer.value = false
  if (value === 'central') {
    router.push('/centraldecomando')
    return
  }

  activePanel.value = value
}

function classLabel(item: ClassOption) {
  const total = Number(item.totalAlunos || 0)
  return `${item.nome} - ${item.anoLetivo} (${total} aluno${total === 1 ? '' : 's'})`
}

function studentLabel(item: StudentOption) {
  return item.turma ? `${item.nome} - ${item.turma}` : `${item.nome} - sem turma`
}

function formatDate(value: string | null) {
  if (!value) return ''
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value.replace(' ', 'T')))
}

function resetForm() {
  form.value = createInitialForm()
  files.value = []
  errorMessage.value = ''
}

function validateForm() {
  if (!form.value.titulo.trim()) return 'Informe o título da notificação.'
  if (!form.value.descricao.trim()) return 'Informe a descrição da notificação.'
  if (!form.value.classes.length && !form.value.alunos.length) {
    return 'Selecione ao menos uma turma ou um aluno.'
  }
  if (form.value.modoPublicacao === 'AGENDAR' && !form.value.dataAgendamento) {
    return 'Informe a data e hora do agendamento.'
  }
  if (isActivity.value && !form.value.dataLimite) {
    return 'Atividades precisam de uma data limite.'
  }
  return ''
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

async function loadPageData() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [configResponse, notificationsResponse] = await Promise.all([
      api.get<NotificationConfig>('/api/notificacoes/configuracoes'),
      api.get<CreatedNotification[]>('/api/notificacoes/gerenciar', {
        params: { limit: 8 },
      }),
    ])
    config.value = configResponse.data
    recentNotifications.value = notificationsResponse.data
  } catch (error: any) {
    errorMessage.value =
      error.response?.data?.detail || 'Não foi possível carregar os dados do formulário.'
  } finally {
    loading.value = false
  }
}

async function submitNotification() {
  const validationError = validateForm()
  if (validationError) {
    errorMessage.value = validationError
    return
  }

  submitting.value = true
  errorMessage.value = ''
  successMessage.value = ''

  const body = new FormData()
  body.append('titulo', form.value.titulo.trim())
  body.append('descricao', form.value.descricao.trim())
  body.append('categoria', form.value.categoria)
  body.append('prioridade', form.value.prioridade)
  body.append('classes', JSON.stringify(form.value.classes))
  body.append('alunos', JSON.stringify(form.value.alunos))
  body.append('solicitar_confirmacao_leitura', String(form.value.solicitarConfirmacaoLeitura))
  body.append('agendada', String(form.value.modoPublicacao === 'AGENDAR'))
  body.append('publicada', String(form.value.modoPublicacao === 'AGORA'))
  body.append('ativa', String(form.value.ativa))
  body.append('permitir_atraso', String(isActivity.value && form.value.permitirAtraso))

  if (form.value.idMateria !== null) body.append('id_materia', String(form.value.idMateria))
  if (form.value.idProfessor !== null) body.append('id_professor', String(form.value.idProfessor))
  if (form.value.modoPublicacao === 'AGENDAR') {
    body.append('data_agendamento', form.value.dataAgendamento)
  }
  if (isActivity.value) body.append('data_limite', form.value.dataLimite)
  files.value.forEach(file => body.append('arquivos', file))

  try {
    const response = await api.post('/api/notificacoes', body)
    successMessage.value =
      `Notificação #${response.data.id} criada para ` +
      `${response.data.totalDestinatarios} destinatário(s).`
    resetForm()
    await loadPageData()
  } catch (error: any) {
    errorMessage.value =
      error.response?.data?.detail || 'Não foi possível criar a notificação.'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchUser()
  loadPageData()
})
</script>

<template>
  <v-app :theme="theme">
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
          :key="item.value"
          :prepend-icon="item.icon"
          :title="item.title"
          :value="item.value"
          :active="activePanel === item.value"
          active-color="error"
          rounded="lg"
          class="mb-1"
          @click="navigate(item.value)"
        />
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

    <v-app-bar flat :border="'b'" :class="theme === 'dark' ? 'bg-surface' : 'bg-white'">
      <v-app-bar-nav-icon class="d-flex d-md-none" @click="mobileDrawer = true" />
      <v-app-bar-title>
        <span class="text-h6 font-weight-bold">{{ appBarTitle }}</span>
      </v-app-bar-title>
      <template #append>
        <v-btn
          :icon="theme === 'dark' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
          variant="text"
          class="mr-1"
          @click="toggleTheme"
        />
      </template>
    </v-app-bar>

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
          <span class="sidebar-app-title">Portal do Professor</span>
        </template>
      </v-list-item>
      <v-divider />
      <v-list density="compact" nav class="mt-2">
        <v-list-item
          v-for="item in navItems"
          :key="item.value"
          :prepend-icon="item.icon"
          :title="item.title"
          :value="item.value"
          :active="activePanel === item.value"
          active-color="error"
          rounded="lg"
          class="mb-1"
          @click="navigate(item.value)"
        />
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

    <v-main>
      <v-container v-if="activePanel === 'create'" fluid class="professor-page pa-4 pa-md-6">
        <section class="hero compact-hero">
          <div>
            <p class="eyebrow">GESTÃO DE NOTIFICAÇÕES</p>
            <h1>Nova notificação</h1>
            <p>
              Monte avisos e atividades com destinatários, prazos e anexos.
            </p>
          </div>
          <div class="hero-stat">
            <v-icon icon="mdi-account-multiple-outline" size="22" />
            <strong>{{ estimatedRecipients }}</strong>
            <span>destinatários</span>
          </div>
        </section>

        <v-alert
          v-if="errorMessage"
          type="error"
          variant="tonal"
          closable
          class="mb-5"
          @click:close="errorMessage = ''"
        >
          {{ errorMessage }}
        </v-alert>

        <v-alert
          v-if="successMessage"
          type="success"
          variant="tonal"
          closable
          class="mb-5"
          @click:close="successMessage = ''"
        >
          {{ successMessage }}
        </v-alert>

        <div v-if="loading" class="loading-card">
          <v-progress-circular indeterminate color="#c7192d" />
          <span>Carregando opções do banco de dados...</span>
        </div>

        <div v-else class="workspace">
          <v-form class="form-column compact-form" @submit.prevent="submitNotification">
            <section class="panel">
              <div class="section-heading">
                <span>01</span>
                <div>
                  <h2>Conteúdo</h2>
                  <p>Defina o que será comunicado aos alunos.</p>
                </div>
              </div>

              <div class="field-grid two-columns">
                <v-select
                  v-model="form.categoria"
                  :items="config.categorias"
                  label="Categoria"
                  variant="outlined"
                  density="compact"
                  color="#c7192d"
                  prepend-inner-icon="mdi-shape-outline"
                />
                <v-select
                  v-model="form.prioridade"
                  :items="config.prioridades"
                  label="Prioridade"
                  variant="outlined"
                  density="compact"
                  color="#c7192d"
                  prepend-inner-icon="mdi-alert-circle-outline"
                />
              </div>

              <v-text-field
                v-model="form.titulo"
                label="Título"
                maxlength="150"
                counter
                variant="outlined"
                density="compact"
                color="#c7192d"
                prepend-inner-icon="mdi-format-title"
              />
              <v-textarea
                v-model="form.descricao"
                label="Descrição"
                maxlength="600"
                counter
                rows="3"
                variant="outlined"
                density="compact"
                color="#c7192d"
                prepend-inner-icon="mdi-text-long"
              />

              <div class="field-grid two-columns">
                <v-select
                  v-model="form.idMateria"
                  :items="config.materias"
                  item-title="nome"
                  item-value="id"
                  label="Matéria (opcional)"
                  clearable
                  variant="outlined"
                  density="compact"
                  color="#c7192d"
                  prepend-inner-icon="mdi-book-open-page-variant-outline"
                />
                <v-select
                  v-model="form.idProfessor"
                  :items="config.professores"
                  item-title="nome"
                  item-value="id"
                  label="Professor responsável (opcional)"
                  clearable
                  variant="outlined"
                  density="compact"
                  color="#c7192d"
                  prepend-inner-icon="mdi-account-tie-outline"
                />
              </div>
            </section>

            <section class="panel">
              <div class="section-heading">
                <span>02</span>
                <div>
                  <h2>Destinatários</h2>
                  <p>Combine turmas completas com alunos específicos.</p>
                </div>
              </div>

              <v-select
                v-model="form.classes"
                :items="config.classes"
                :item-title="classLabel"
                item-value="id"
                label="Turmas"
                multiple
                chips
                closable-chips
                clearable
                variant="outlined"
                density="compact"
                color="#c7192d"
                prepend-inner-icon="mdi-google-classroom"
              />
              <v-autocomplete
                v-model="form.alunos"
                :items="config.alunos"
                :item-title="studentLabel"
                item-value="id"
                label="Alunos específicos"
                multiple
                chips
                closable-chips
                clearable
                variant="outlined"
                density="compact"
                color="#c7192d"
                prepend-inner-icon="mdi-account-search-outline"
              />

              <div class="selection-summary">
                <span>
                  <v-icon icon="mdi-google-classroom" />
                  {{ selectedClasses.length }} turma(s)
                </span>
                <span>
                  <v-icon icon="mdi-account-check-outline" />
                  {{ selectedStudents.length }} aluno(s) direto(s)
                </span>
                <strong>{{ estimatedRecipients }} destinatário(s) únicos</strong>
              </div>
            </section>

            <section class="panel">
              <div class="section-heading">
                <span>03</span>
                <div>
                  <h2>Publicação e regras</h2>
                  <p>Controle quando a mensagem aparece e como ela deve ser tratada.</p>
                </div>
              </div>

              <v-radio-group v-model="form.modoPublicacao" inline color="#c7192d" density="compact" hide-details>
                <v-radio label="Publicar agora" value="AGORA" />
                <v-radio label="Agendar" value="AGENDAR" />
                <v-radio label="Salvar rascunho" value="RASCUNHO" />
              </v-radio-group>

              <div class="field-grid two-columns">
                <v-text-field
                  v-if="form.modoPublicacao === 'AGENDAR'"
                  v-model="form.dataAgendamento"
                  type="datetime-local"
                  label="Data do agendamento"
                  variant="outlined"
                  density="compact"
                  color="#c7192d"
                  prepend-inner-icon="mdi-calendar-clock-outline"
                />
                <v-text-field
                  v-if="isActivity"
                  v-model="form.dataLimite"
                  type="datetime-local"
                  label="Prazo da atividade"
                  variant="outlined"
                  density="compact"
                  color="#c7192d"
                  prepend-inner-icon="mdi-calendar-alert-outline"
                />
              </div>

              <div class="switch-grid">
                <v-switch
                  v-model="form.solicitarConfirmacaoLeitura"
                  label="Solicitar confirmação de leitura"
                  color="#c7192d"
                  inset
                  hide-details
                />
                <v-switch
                  v-if="isActivity"
                  v-model="form.permitirAtraso"
                  label="Permitir entrega após o prazo"
                  color="#c7192d"
                  inset
                  hide-details
                />
                <v-switch
                  v-model="form.ativa"
                  label="Notificação ativa"
                  color="#c7192d"
                  inset
                  hide-details
                />
              </div>

              <v-file-input
                v-model="files"
                label="Anexos"
                multiple
                chips
                show-size
                variant="outlined"
                density="compact"
                color="#c7192d"
                prepend-icon=""
                prepend-inner-icon="mdi-paperclip"
                hint="Até 10 MB por arquivo"
                persistent-hint
              />
            </section>

            <div class="form-actions">
              <v-btn variant="text" prepend-icon="mdi-refresh" @click="resetForm">
                Limpar
              </v-btn>
              <v-btn
                type="submit"
                color="#c7192d"
                variant="flat"
                prepend-icon="mdi-send-outline"
                :loading="submitting"
              >
                Criar notificação
              </v-btn>
            </div>
          </v-form>

          <aside class="side-column">
            <section class="preview-card">
              <div class="preview-label">
                <span>PRÉVIA</span>
                <v-chip size="small" :color="priorityColor" variant="flat">
                  {{ form.prioridade }}
                </v-chip>
              </div>
              <div class="preview-icon" :style="{ backgroundColor: priorityColor }">
                <v-icon :icon="isActivity ? 'mdi-clipboard-text-outline' : 'mdi-bullhorn-outline'" />
              </div>
              <span class="preview-subject">{{ selectedSubject }}</span>
              <h3>{{ form.titulo || 'Título da sua notificação' }}</h3>
              <p>
                {{ form.descricao || 'A descrição aparecerá aqui para você conferir antes de publicar.' }}
              </p>
              <div class="preview-meta">
                <span><v-icon icon="mdi-shape-outline" /> {{ form.categoria }}</span>
                <span><v-icon icon="mdi-send-clock-outline" /> {{ publicationLabel }}</span>
                <span v-if="files.length">
                  <v-icon icon="mdi-paperclip" /> {{ files.length }} anexo(s)
                </span>
              </div>
            </section>

            <section class="recent-card recent-card-collapsible">
              <div class="recent-heading">
                <div>
                  <span>HISTÓRICO</span>
                  <h2>Criações recentes</h2>
                </div>
                <div class="recent-actions">
                  <v-chip size="x-small" color="#c7192d" variant="tonal">
                    {{ recentNotifications.length }}
                  </v-chip>
                  <v-btn
                    icon="mdi-refresh"
                    variant="text"
                    size="small"
                    aria-label="Atualizar histórico"
                    @click="loadPageData"
                  />
                  <v-btn
                    :icon="showRecent ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                    variant="tonal"
                    color="#c7192d"
                    size="small"
                    aria-label="Abrir criações recentes"
                    @click="showRecent = !showRecent"
                  />
                </div>
              </div>

              <v-expand-transition>
                <div v-if="showRecent" class="recent-content">
                  <div v-if="!recentNotifications.length" class="empty-history">
                    <v-icon icon="mdi-bell-sleep-outline" />
                    <span>Nenhuma notificação criada.</span>
                  </div>

                  <article
                    v-for="notification in recentNotifications"
                    :key="notification.id"
                    class="history-item"
                  >
                    <div class="history-topline">
                      <span>#{{ notification.id }} · {{ notification.categoria }}</span>
                      <v-chip
                        size="x-small"
                        :color="notification.ativa ? 'success' : 'grey'"
                        variant="tonal"
                      >
                        {{
                          notification.agendada
                            ? 'Agendada'
                            : notification.publicada
                              ? 'Publicada'
                              : 'Rascunho'
                        }}
                      </v-chip>
                    </div>
                    <h3>{{ notification.titulo }}</h3>
                    <p>
                      {{ notification.totalDestinatarios }} destinatário(s) ·
                      {{ notification.totalAnexos }} anexo(s)
                    </p>
                    <time>
                      {{
                        formatDate(
                          notification.agendada
                            ? notification.dataAgendamento
                            : notification.dataMensagem,
                        )
                      }}
                    </time>
                  </article>
                </div>
              </v-expand-transition>
            </section>
          </aside>
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
.sidebar-dark { background: #1c1c1e !important; }

.professor-page {
  min-height: 100%;
  background: #f5f3f0;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin: 0 auto 20px;
  max-width: 1440px;
}

.compact-hero {
  padding: 18px 22px;
  background: #fff;
  border: 1px solid #e4dfda;
}

.eyebrow,
.recent-heading span {
  margin: 0 0 6px;
  color: #c7192d;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.16em;
}

.hero h1 {
  max-width: 760px;
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(28px, 3.5vw, 42px);
  font-weight: 500;
  line-height: 1.05;
}

.hero p:not(.eyebrow) {
  max-width: 760px;
  margin: 8px 0 0;
  color: #67615c;
  font-size: 14px;
  line-height: 1.45;
}

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

.loading-card {
  min-height: 260px;
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 18px;
  background: white;
  border: 1px solid #e4dfda;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.9fr) minmax(280px, 0.7fr);
  gap: 18px;
  align-items: start;
  max-width: 1440px;
  margin: 0 auto;
}

.form-column {
  display: grid;
  gap: 12px;
}

.panel,
.preview-card,
.recent-card {
  background: white;
  border: 1px solid #e4dfda;
  box-shadow: 0 18px 50px rgba(42, 31, 28, 0.04);
}

.panel {
  padding: 18px;
}

.section-heading {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
}

.section-heading > span {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  color: #c7192d;
  border: 1px solid #c7192d;
  font-size: 12px;
  font-weight: 800;
}

.section-heading h2,
.recent-heading h2 {
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 20px;
  font-weight: 500;
}

.section-heading p {
  margin: 2px 0 0;
  color: #77716c;
  font-size: 12px;
}

.field-grid {
  display: grid;
  gap: 10px;
}

.two-columns {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.switch-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 2px 18px;
  margin: 0 0 10px;
}

.selection-summary {
  padding: 10px 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  align-items: center;
  background: #f7f5f2;
  border-left: 3px solid #c7192d;
  color: #625c57;
  font-size: 12px;
}

.selection-summary span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.selection-summary strong {
  margin-left: auto;
  color: #202124;
}

.form-actions {
  padding: 4px 0 0;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.side-column {
  display: grid;
  gap: 12px;
  position: sticky;
  top: 16px;
}

.preview-card,
.recent-card {
  padding: 18px;
}

.preview-label,
.recent-heading,
.history-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.preview-label > span,
.history-topline > span {
  color: #8a837d;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.14em;
}

.preview-icon {
  width: 42px;
  height: 42px;
  margin: 18px 0 14px;
  display: grid;
  place-items: center;
  color: white;
}

.preview-subject {
  color: #c7192d;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.preview-card h3 {
  margin: 8px 0 8px;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 22px;
  font-weight: 500;
  line-height: 1.16;
}

.preview-card > p {
  min-height: 44px;
  margin: 0;
  color: #68615c;
  font-size: 13px;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.preview-meta {
  margin-top: 14px;
  padding-top: 12px;
  display: grid;
  gap: 7px;
  border-top: 1px solid #ebe7e3;
  color: #77716c;
  font-size: 12px;
}

.preview-meta span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recent-heading {
  margin-bottom: 0;
}

.recent-heading span {
  display: block;
  margin-bottom: 3px;
}

.recent-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.recent-content {
  margin-top: 10px;
  max-height: 360px;
  overflow: auto;
}

.history-item {
  padding: 12px 0;
  border-top: 1px solid #ebe7e3;
}

.history-item h3 {
  margin: 7px 0 4px;
  font-size: 14px;
  line-height: 1.35;
}

.history-item p,
.history-item time {
  color: #817a74;
  font-size: 12px;
}

.history-item p {
  margin: 0 0 6px;
}

.empty-history {
  min-height: 90px;
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 10px;
  color: #8a837d;
}

.compact-form :deep(.v-input) {
  margin-bottom: 2px;
}

.compact-form :deep(.v-input__details) {
  min-height: 14px;
  padding-top: 1px;
}

.compact-form :deep(.v-field__input) {
  font-size: 14px;
}

.compact-form :deep(.v-selection-control) {
  min-height: 34px;
}

@media (max-width: 1024px) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .side-column {
    position: static;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 959px) {
  .v-navigation-drawer--permanent {
    display: none !important;
  }
}

@media (max-width: 700px) {
  .hero {
    align-items: stretch;
    flex-direction: column;
  }

  .hero-stat {
    min-width: 0;
  }

  .two-columns,
  .switch-grid,
  .side-column {
    grid-template-columns: 1fr;
  }

  .selection-summary strong {
    width: 100%;
    margin-left: 0;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .form-actions :deep(.v-btn) {
    width: 100%;
  }
}
</style>
