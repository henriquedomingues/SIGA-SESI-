import { createApp } from 'vue'
import { createPinia } from 'pinia'


// Vuetify
import vuetify from './plugins/vuetify'
import '@mdi/font/css/materialdesignicons.css'

// App
import App from './App.vue'
import router from './router'

// Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'

library.add(fas)

const app = createApp(App)

// 👇 CONFIGURA TUDO ANTES
app.use(vuetify)
app.use(createPinia())
app.use(router)

app.component('font-awesome-icon', FontAwesomeIcon)

// 👇 MONTA UMA VEZ SÓ
app.mount('#app')