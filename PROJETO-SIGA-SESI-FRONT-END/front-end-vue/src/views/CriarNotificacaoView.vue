<script setup lang="ts">
//chat gpt fes - inicio da logica da view de criacao de notificacoes
import { computed, onMounted, ref } from 'vue'
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

const config = ref<NotificationConfig>(emptyConfig)
const form = ref(createInitialForm())
const files = ref<File[]>([])
const recentNotifications = ref<CreatedNotification[]>([])
const loading = ref(true)
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

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
  body.append(
    'solicitar_confirmacao_leitura',
    String(form.value.solicitarConfirmacaoLeitura),
  )
  body.append('agendada', String(form.value.modoPublicacao === 'AGENDAR'))
  body.append('publicada', String(form.value.modoPublicacao === 'AGORA'))
  body.append('ativa', String(form.value.ativa))
  body.append('permitir_atraso', String(isActivity.value && form.value.permitirAtraso))

  if (form.value.idMateria !== null) {
    body.append('id_materia', String(form.value.idMateria))
  }
  if (form.value.idProfessor !== null) {
    body.append('id_professor', String(form.value.idProfessor))
  }
  if (form.value.modoPublicacao === 'AGENDAR') {
    body.append('data_agendamento', form.value.dataAgendamento)
  }
  if (isActivity.value) {
    body.append('data_limite', form.value.dataLimite)
  }
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

onMounted(loadPageData)
//chat gpt fes - fim da logica da view de criacao de notificacoes
</script>

<template>
  <!-- chat gpt fes - inicio da interface de criacao de notificacoes -->
  <v-app>
    <div class="page-shell">
      <header class="topbar">
        <div class="brand">
          <div class="brand-mark">SESI</div>
          <div>
            <strong>SIGA SESI</strong>
            <span>Central de comunicação</span>
          </div>
        </div>
        <v-chip color="#c7192d" variant="tonal" prepend-icon="mdi-lock-open-outline">
          Acesso público temporário
        </v-chip>
      </header>

      <main class="content">
        <section class="hero">
          <div>
            <p class="eyebrow">GESTÃO DE NOTIFICAÇÕES</p>
            <h1>Crie a mensagem certa para cada turma.</h1>
            <p>
              Publique avisos e atividades, escolha os destinatários, defina prazos,
              prioridade, confirmação de leitura e anexos em um único lugar.
            </p>
          </div>
          <div class="hero-stat">
            <v-icon icon="mdi-account-multiple-outline" size="30" />
            <strong>{{ estimatedRecipients }}</strong>
            <span>destinatários selecionados</span>
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
          <v-form class="form-column" @submit.prevent="submitNotification">
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
                  color="#c7192d"
                  prepend-inner-icon="mdi-shape-outline"
                />
                <v-select
                  v-model="form.prioridade"
                  :items="config.prioridades"
                  label="Prioridade"
                  variant="outlined"
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
                color="#c7192d"
                prepend-inner-icon="mdi-format-title"
              />
              <v-textarea
                v-model="form.descricao"
                label="Descrição"
                maxlength="600"
                counter
                rows="5"
                variant="outlined"
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

              <v-radio-group v-model="form.modoPublicacao" inline color="#c7192d">
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
                  color="#c7192d"
                  prepend-inner-icon="mdi-calendar-clock-outline"
                />
                <v-text-field
                  v-if="isActivity"
                  v-model="form.dataLimite"
                  type="datetime-local"
                  label="Prazo da atividade"
                  variant="outlined"
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
                color="#c7192d"
                prepend-icon=""
                prepend-inner-icon="mdi-paperclip"
                hint="Até 10 MB por arquivo"
                persistent-hint
              />
            </section>

            <div class="form-actions">
              <v-btn
                variant="text"
                size="large"
                prepend-icon="mdi-refresh"
                @click="resetForm"
              >
                Limpar
              </v-btn>
              <v-btn
                type="submit"
                color="#c7192d"
                size="large"
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
                <v-icon
                  :icon="isActivity ? 'mdi-clipboard-text-outline' : 'mdi-bullhorn-outline'"
                />
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

            <section class="recent-card">
              <div class="recent-heading">
                <div>
                  <span>HISTÓRICO</span>
                  <h2>Criações recentes</h2>
                </div>
                <v-btn
                  icon="mdi-refresh"
                  variant="text"
                  size="small"
                  aria-label="Atualizar histórico"
                  @click="loadPageData"
                />
              </div>

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
            </section>
          </aside>
        </div>
      </main>
    </div>
  </v-app>
  <!-- chat gpt fes - fim da interface de criacao de notificacoes -->
</template>

<style scoped>
/* chat gpt fes - inicio dos estilos da view de criacao de notificacoes */
:global(body) {
  margin: 0;
  background: #f5f3f0;
  color: #202124;
  font-family: Inter, "Segoe UI", sans-serif;
}

.page-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at 90% 8%, rgba(199, 25, 45, 0.08), transparent 24rem),
    #f5f3f0;
}

.topbar {
  min-height: 76px;
  padding: 14px clamp(20px, 5vw, 72px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid #e4dfda;
  backdrop-filter: blur(12px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 13px;
}

.brand-mark {
  padding: 9px 12px;
  color: white;
  background: #c7192d;
  font-size: 18px;
  font-weight: 900;
  letter-spacing: 0.08em;
  line-height: 1;
}

.brand strong,
.brand span {
  display: block;
}

.brand strong {
  letter-spacing: 0.08em;
}

.brand span {
  margin-top: 2px;
  color: #77716c;
  font-size: 12px;
}

.content {
  width: min(1440px, calc(100% - 40px));
  margin: 0 auto;
  padding: 56px 0 72px;
}

.hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 40px;
  margin-bottom: 36px;
}

.eyebrow,
.recent-heading span {
  margin: 0 0 10px;
  color: #c7192d;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.16em;
}

.hero h1 {
  max-width: 760px;
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(36px, 5vw, 64px);
  font-weight: 500;
  line-height: 1.02;
}

.hero p:not(.eyebrow) {
  max-width: 760px;
  margin: 18px 0 0;
  color: #67615c;
  font-size: 17px;
  line-height: 1.7;
}

.hero-stat {
  min-width: 210px;
  padding: 24px;
  color: white;
  background: #222222;
}

.hero-stat strong,
.hero-stat span {
  display: block;
}

.hero-stat strong {
  margin-top: 16px;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 44px;
  line-height: 1;
}

.hero-stat span {
  margin-top: 8px;
  color: #c9c5c1;
  font-size: 13px;
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
  grid-template-columns: minmax(0, 1.65fr) minmax(320px, 0.75fr);
  gap: 28px;
  align-items: start;
}

.form-column {
  display: grid;
  gap: 20px;
}

.panel,
.preview-card,
.recent-card {
  background: white;
  border: 1px solid #e4dfda;
  box-shadow: 0 18px 50px rgba(42, 31, 28, 0.04);
}

.panel {
  padding: clamp(22px, 4vw, 36px);
}

.section-heading {
  display: flex;
  gap: 16px;
  margin-bottom: 28px;
}

.section-heading > span {
  width: 38px;
  height: 38px;
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
  font-size: 26px;
  font-weight: 500;
}

.section-heading p {
  margin: 5px 0 0;
  color: #77716c;
  font-size: 14px;
}

.field-grid {
  display: grid;
  gap: 16px;
}

.two-columns {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.switch-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 22px;
  margin: 4px 0 26px;
}

.selection-summary {
  padding: 16px 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 14px 22px;
  align-items: center;
  background: #f7f5f2;
  border-left: 3px solid #c7192d;
  color: #625c57;
  font-size: 13px;
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
  padding: 12px 0;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.side-column {
  display: grid;
  gap: 20px;
  position: sticky;
  top: 24px;
}

.preview-card,
.recent-card {
  padding: 26px;
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
  width: 52px;
  height: 52px;
  margin: 36px 0 22px;
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
  margin: 10px 0 12px;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 28px;
  font-weight: 500;
  line-height: 1.16;
}

.preview-card > p {
  min-height: 68px;
  margin: 0;
  color: #68615c;
  line-height: 1.6;
  overflow-wrap: anywhere;
}

.preview-meta {
  margin-top: 26px;
  padding-top: 18px;
  display: grid;
  gap: 10px;
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
  margin-bottom: 12px;
}

.recent-heading span {
  display: block;
  margin-bottom: 5px;
}

.history-item {
  padding: 18px 0;
  border-top: 1px solid #ebe7e3;
}

.history-item h3 {
  margin: 9px 0 5px;
  font-size: 15px;
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
  min-height: 140px;
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 10px;
  color: #8a837d;
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

@media (max-width: 700px) {
  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .content {
    width: min(100% - 24px, 1440px);
    padding-top: 34px;
  }

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
/* chat gpt fes - fim dos estilos da view de criacao de notificacoes */
</style>
