  <script setup>
  import { ref, computed, onMounted, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import axios from 'axios'
  import api from "@/services/api"

  const router = useRouter()

  const form = ref({
    login: '',
    senha: '',
    escola: null,
    tipoUser: 'Aluno'
  })

  const cargos = ref([])
  const escolas = ref([])

  const errors = ref({
    login: '',
    senha: '',
    escola: '',
    geral: ''
  })

  const loginPlaceholder = computed(() => {
    return form.value.tipoUser === 'Aluno'
      ? 'RM / Email / CPF'
      : 'Email / CPF'
  })

  /* =========================
    🔥 VALIDAÇÕES
  ========================= */

  const isEmail = (value) => /\S+@\S+\.\S+/.test(value)

  const isCPF = (cpf) => {
    cpf = cpf.replace(/[^\d]+/g, '')
    if (cpf.length !== 11) return false
    if (/^(\d)\1+$/.test(cpf)) return false
    return true
  }

  const isRM = (value) => /^\d{1,8}$/.test(value)

  /* 🔥 FUNÇÃO PROFISSIONAL */
  const parseLogin = (login) => {

    if (form.value.tipoUser  === 'Aluno'){
      if (isEmail(login)) {
      return { emailUser: login }
      }

      if (isCPF(login)) {
      return { cpfUser: login }
      }

      if (isRM(login)) {
      return { rm: login }
      } 

      throw new Error('Digite um Email, CPF ou RM válido')  
    }
    else {
      if (isEmail(login)) {
      return { emailUser: login }
      }

      if (isCPF(login)) {
      return { cpfUser: login }
      }
      throw new Error('Digite um Email ou CPF válido')
    }

    
  }

  /* ========================= */

  const isFormValid = computed(() => {
    return (
      form.value.login &&
      form.value.senha &&
      form.value.escola &&
      form.value.tipoUser
    )
  })

  const onCargoChange = () => {
    form.value.login = ''
    errors.value.login = ''
  }

  /* limpa erro ao digitar */
  watch(() => form.value.login, () => errors.value.login = '')
  watch(() => form.value.senha, () => errors.value.senha = '')
  watch(() => form.value.escola, () => errors.value.escola = '')

 onMounted(async () => {
  try {
    const res = await api.get('/escolas') // substitui axios.get
    escolas.value = res.data
    cargos.value = ['Aluno', 'Professor']
  } catch (err) {
    console.error(err)
  }
})


  const submit = async () => {
  errors.value = {
    login: '',
    senha: '',
    escola: '',
    geral: ''
  }

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

  let payload = {
    password: form.value.senha,
    tipoUser: form.value.tipoUser.toUpperCase(),
    escolaId: form.value.escola
  }

  try {
    const loginData = parseLogin(form.value.login)
    Object.assign(payload, loginData)

    const res = await api.post("/auth/login", payload)

    localStorage.setItem("token", res.data.access_token)
    localStorage.setItem("tipoUser", res.data.tipoUser)

    if (res.data.tipoUser === "ALUNO") {
      router.push("/aluno")
    } else if (res.data.tipoUser === "PROFESSOR") {
      router.push("/professor")
    } else {
      router.push("/")
    }

  } catch (error) {

  // erro de validação (parseLogin)
  if (error.message && !error.response) {
    errors.value.login = error.message
    return
  }

  // 🔥 AQUI ENTRA O TRECHO QUE VOCÊ PERGUNTOU
  if (error.response?.status === 401 || error.response?.status === 400) {
    errors.value.geral = 'Usuário ou senha incorretos'
    return
  }

  // outros erros
  if (error.response) {
    errors.value.geral =
      error.response.data.detail || 'Erro ao fazer login'
  } else {
    errors.value.geral = 'Erro no servidor'
  }
}
}
  </script>

  <template>
    <v-app>
      <div class="login-container">

        <div class="lines">
          <div class="line" v-for="i in 10" :key="i"></div>
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
                      @update:modelValue="onCargoChange"
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
                  <p>Entrar</p>
                </v-btn>

              
                <div class="links">
                  <a class="forgot" @click="goToRecover">
                    Esqueceu a senha?
                  </a>
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
    border-radius: 16px;
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
  }

  p {
    color: white;
  }

  .links {
    margin-top: 15px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .forgot {
    color: #1e88e5;
    cursor: pointer;
    font-size: 14px;
  }

  /* erro geral */
  .error-geral {
    color: red;
    font-size: 14px;
    margin-top: 5px;
    text-align: center;
  }

  /* mensagens alinhadas */
  :deep(.v-messages) {
    
    text-align: left !important;
  }

  /* linhas animadas */
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