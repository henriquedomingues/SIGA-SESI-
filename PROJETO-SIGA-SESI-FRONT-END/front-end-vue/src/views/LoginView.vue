<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { jwtDecode } from 'jwt-decode'
import api from '@/services/api'

type UserRole = 'Aluno' | 'Professor'

type School = {
  id: number
  nome: string
}

type LoginPayload = {
  password: string
  tipoUser: string
  escolaId: number
  emailUser?: string
  cpfUser?: string
  rm?: string
}

type TokenPayload = {
  tipoUser: 'ALUNO' | 'PROFESSOR'
}

type ApiError = {
  message?: string
  response?: {
    status?: number
    data?: {
      detail?: string
    }
  }
}

const router = useRouter()

const form = ref({
  login: '',
  senha: '',
  escola: null as number | null,
  tipoUser: 'Aluno' as UserRole,
})

const cargos = ref<UserRole[]>([])
const escolas = ref<School[]>([])

const errors = ref({
  login: '',
  senha: '',
  escola: '',
  geral: '',
})

const loginPlaceholder = computed(() =>
  form.value.tipoUser === 'Aluno' ? 'RM / Email / CPF' : 'Email / CPF',
)

const isFormValid = computed(() =>
  Boolean(form.value.login && form.value.senha && form.value.escola && form.value.tipoUser),
)

function isEmail(value: string) {
  return /\S+@\S+\.\S+/.test(value)
}

function isCPF(value: string) {
  const cpf = value.replace(/[^\d]+/g, '')
  return cpf.length === 11 && !/^(\d)\1+$/.test(cpf)
}

function isRM(value: string) {
  return /^\d{1,8}$/.test(value)
}

function parseLogin(login: string): Pick<LoginPayload, 'emailUser' | 'cpfUser' | 'rm'> {
  if (isEmail(login)) return { emailUser: login }
  if (isCPF(login)) return { cpfUser: login }
  if (form.value.tipoUser === 'Aluno' && isRM(login)) return { rm: login }

  throw new Error(
    form.value.tipoUser === 'Aluno'
      ? 'Digite um Email, CPF ou RM válido'
      : 'Digite um Email ou CPF válido',
  )
}

function resetErrors() {
  errors.value = {
    login: '',
    senha: '',
    escola: '',
    geral: '',
  }
}

function onCargoChange() {
  form.value.login = ''
  errors.value.login = ''
}

function goToRecover() {
  errors.value.geral = 'Recuperação de senha ainda não disponível'
}

watch(() => form.value.login, () => { errors.value.login = '' })
watch(() => form.value.senha, () => { errors.value.senha = '' })
watch(() => form.value.escola, () => { errors.value.escola = '' })

onMounted(async () => {
  try {
    const response = await api.get<School[]>('/escolas')
    escolas.value = response.data
    cargos.value = ['Aluno', 'Professor']
  } catch (error) {
    console.error(error)
  }
})

async function submit() {
  resetErrors()

  if (!form.value.login) {
    errors.value.login = 'Digite o login'
    return
  }

  if (!form.value.senha) {
    errors.value.senha = 'Digite a senha'
    return
  }

  if (!form.value.escola) {
    errors.value.escola = 'Selecione a escola'
    return
  }

  const payload: LoginPayload = {
    password: form.value.senha,
    tipoUser: form.value.tipoUser.toUpperCase(),
    escolaId: form.value.escola,
    ...parseLogin(form.value.login),
  }

  try {
    const response = await api.post<{ token: string }>('/auth/login', payload)
    const decoded = jwtDecode<TokenPayload>(response.data.token)
    const tipoUser = decoded.tipoUser

    localStorage.setItem('token', response.data.token)
    localStorage.setItem('tipoUser', tipoUser)

    if (tipoUser === 'ALUNO') {
      router.push('/aluno')
    } else if (tipoUser === 'PROFESSOR') {
      router.push('/professor')
    } else {
      router.push('/')
    }
  } catch (error) {
    const apiError = error as ApiError

    if (apiError.message && !apiError.response) {
      errors.value.login = apiError.message
      return
    }

    if (apiError.response?.status === 401 || apiError.response?.status === 400) {
      errors.value.geral = 'Usuário ou senha incorretos'
      return
    }

    errors.value.geral = apiError.response?.data?.detail || 'Erro ao fazer login'
  }
}
</script>

<template>
  <v-app>
    <div class="login-container">
      <div class="lines">
        <div v-for="i in 10" :key="i" class="line" />
      </div>

      <v-container class="fill-height d-flex align-center justify-center">
        <div class="content-wrapper">
          <div class="logo-wrapper">
            <img class="logo" src="../images/Logo_SESI_vermelho.jpg" alt="Logo Sesi">
          </div>

          <v-card class="login-card" elevation="10">
            <v-card-text>
              <v-text-field
                v-model="form.login"
                :placeholder="loginPlaceholder"
                :error-messages="errors.login"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                density="comfortable"
                class="input"
              />

              <v-text-field
                v-model="form.senha"
                placeholder="Digite sua senha"
                type="password"
                :error-messages="errors.senha"
                prepend-inner-icon="mdi-lock"
                variant="outlined"
                density="comfortable"
                class="input"
              />

              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-select
                    v-model="form.escola"
                    :items="escolas"
                    item-title="nome"
                    item-value="id"
                    label="Escola"
                    :error-messages="errors.escola"
                    variant="outlined"
                    density="comfortable"
                  />
                </v-col>

                <v-col cols="12" sm="6">
                  <v-select
                    v-model="form.tipoUser"
                    :items="cargos"
                    label="Cargo"
                    variant="outlined"
                    density="comfortable"
                    @update:model-value="onCargoChange"
                  />
                </v-col>
              </v-row>

              <div v-if="errors.geral" class="error-geral">
                {{ errors.geral }}
              </div>

              <v-btn
                block
                size="large"
                class="btn-login"
                :disabled="!isFormValid"
                @click="submit"
              >
                Entrar
              </v-btn>

              <div class="links">
                <button type="button" class="forgot" @click="goToRecover">
                  Esqueceu a senha?
                </button>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-container>
    </div>
  </v-app>
</template>

<style scoped>
.login-container {
  position: relative;
  height: 100vh;
  background-color: #0a0a0a;
  overflow: hidden;
}

.content-wrapper {
  width: 100%;
  max-width: 420px;
  text-align: center;
  z-index: 2;
}

.logo-wrapper {
  margin-bottom: 20px;
}

.logo {
  width: 300px;
  max-width: 80%;
}

.login-card {
  border-radius: 8px;
  padding: 20px;
  background: #f5f5f5;
}

.input {
  margin-bottom: 10px;
}

.btn-login {
  margin-top: 10px;
  border-radius: 8px;
  height: 45px;
  background-color: #ff0000 !important;
  color: white;
}

.links {
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.forgot {
  border: 0;
  background: transparent;
  color: #1e88e5;
  cursor: pointer;
  font-size: 14px;
}

.forgot:hover {
  text-decoration: underline;
}

.error-geral {
  color: red;
  font-size: 14px;
  margin-top: 5px;
  text-align: center;
}

:deep(.v-messages) {
  text-align: left !important;
}

.lines {
  position: absolute;
  inset: 0;
  display: flex;
  justify-content: space-between;
  background-color: #0a0a0aec;
}

.line {
  width: 1px;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.line::after {
  content: '';
  position: absolute;
  height: 15vh;
  width: 100%;
  top: -50%;
  background: linear-gradient(to bottom, rgba(255,255,255,0), #ff0000 75%, #ff0000);
  animation: drop 7s infinite;
}

.line:nth-child(1)::after { animation-delay: 0.5s; }
.line:nth-child(2)::after { animation-delay: 1s; }
.line:nth-child(3)::after { animation-delay: 1.5s; }
.line:nth-child(4)::after { animation-delay: 2s; }
.line:nth-child(5)::after { animation-delay: 2.5s; }
.line:nth-child(6)::after { animation-delay: 3s; }
.line:nth-child(7)::after { animation-delay: 3.5s; }
.line:nth-child(8)::after { animation-delay: 4s; }
.line:nth-child(9)::after { animation-delay: 4.5s; }
.line:nth-child(10)::after { animation-delay: 5s; }

@keyframes drop {
  0% { top: -50%; }
  100% { top: 110%; }
}

@media (max-width: 600px) {
  .logo {
    width: 140px;
  }
}
</style>
