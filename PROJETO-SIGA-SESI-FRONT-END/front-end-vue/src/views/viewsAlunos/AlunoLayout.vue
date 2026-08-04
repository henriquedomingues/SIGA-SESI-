<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthenticatedUser } from '@/composables/useAuthenticatedUser'

type NavItem = {
  title: string
  value: string
  icon: string
  to: string
}

const props = withDefaults(defineProps<{
  title?: string
  eyebrow?: string
  description?: string
  active?: 'home' | 'notifications'
}>(), {
  title: 'Portal do Aluno',
  eyebrow: 'AREA DO ALUNO',
  description: '',
  active: 'notifications',
})

const router = useRouter()
const theme = ref('light')
const drawer = ref(true)
const rail = ref(false)
const mobileDrawer = ref(false)
const { currentUser, userInitials, fetchUser } = useAuthenticatedUser()

const navItems: NavItem[] = [
  { title: 'Inicio', value: 'home', icon: 'mdi-view-dashboard-outline', to: '/aluno' },
  { title: 'Notificacoes', value: 'notifications', icon: 'mdi-bell-outline', to: '/aluno' },
]

function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

function navigate(item: NavItem) {
  mobileDrawer.value = false
  router.push(item.to)
}

onMounted(fetchUser)
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
          :active="props.active === item.value"
          active-color="error"
          rounded="lg"
          class="mb-1"
          @click="navigate(item)"
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
        <span class="text-h6 font-weight-bold">{{ props.title }}</span>
      </v-app-bar-title>
      <template #append>
        <v-btn
          :icon="theme === 'dark' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
          variant="text"
          class="mr-1"
          @click="toggleTheme"
        />
        <slot name="app-bar-actions" />
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
          <span class="sidebar-app-title">Portal do Aluno</span>
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
          :active="props.active === item.value"
          active-color="error"
          rounded="lg"
          class="mb-1"
          @click="navigate(item)"
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
      <v-container fluid class="student-page pa-4 pa-md-6">
        <section class="hero compact-hero">
          <div>
            <p class="eyebrow">{{ props.eyebrow }}</p>
            <h1>{{ props.title }}</h1>
            <p v-if="props.description">{{ props.description }}</p>
          </div>
          <slot name="hero-action" />
        </section>

        <slot />
      </v-container>
    </v-main>
  </v-app>
</template>

<style scoped>
.sesi-logo-badge {
  background: #c41e2a;
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

.student-page {
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

.eyebrow {
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
}
</style>
