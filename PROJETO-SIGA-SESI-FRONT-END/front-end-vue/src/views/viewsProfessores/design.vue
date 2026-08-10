<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppTheme } from '@/composables/useAppTheme'
import { useAuthenticatedUser } from '@/composables/useAuthenticatedUser'

type NavItem = {
  title: string
  value: string
  icon: string
  to: string
}

type ProfileMenuItem = {
  title: string
  icon: string
  action: () => void
}

const props = withDefaults(defineProps<{
  title?: string
  eyebrow?: string
  description?: string
  active?: 'notifications' | 'central'
}>(), {
  title: 'Portal do Professor',
  eyebrow: 'AREA DO PROFESSOR',
  description: '',
  active: 'central',
})

const router = useRouter()
const drawer = ref(true)
const rail = ref(false)
const mobileDrawer = ref(false)
const { theme, isDark, toggleTheme } = useAppTheme()
const { currentUser, userInitials, fetchUser } = useAuthenticatedUser()

const navItems: NavItem[] = [
  { title: 'Notificações', value: 'notifications', icon: 'mdi-bell-outline', to: '/professor' },
  { title: 'Central de Controle', value: 'central', icon: 'mdi-view-dashboard-outline', to: '/centraldecomando' },
]

const profileMenuItems: ProfileMenuItem[] = [
  { title: 'Sair da conta', icon: 'mdi-logout', action: logout },
]

function navigate(item: NavItem) {
  mobileDrawer.value = false
  router.push(item.to)
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('tipoUser')
  router.replace('/')
}

onMounted(fetchUser)
</script>

<template>
  <v-app :theme="theme" :class="['professor-shell', { 'theme-dark': isDark }]">
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      permanent
      :class="['sidebar-drawer', isDark ? 'sidebar-dark' : 'sidebar-light']"
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
        <v-menu location="top end" transition="scale-transition">
          <template #activator="{ props: menuProps }">
            <v-list-item
              v-bind="menuProps"
              :title="rail ? undefined : currentUser.name"
              :subtitle="rail ? undefined : currentUser.turma"
              nav
              class="profile-trigger py-3"
            >
              <template #prepend>
                <v-avatar color="error" size="34">
                  <span class="text-caption font-weight-bold text-white">{{ userInitials }}</span>
                </v-avatar>
              </template>
            </v-list-item>
          </template>

          <v-list class="profile-menu" density="compact" min-width="210">
            <v-list-item class="profile-menu-header" :title="currentUser.name" :subtitle="currentUser.turma">
              <template #prepend>
                <v-avatar color="error" size="30">
                  <span class="text-caption font-weight-bold text-white">{{ userInitials }}</span>
                </v-avatar>
              </template>
            </v-list-item>
            <v-divider />
            <v-list-item
              v-for="item in profileMenuItems"
              :key="item.title"
              :prepend-icon="item.icon"
              :title="item.title"
              @click="item.action"
            />
          </v-list>
        </v-menu>
      </template>
    </v-navigation-drawer>

    <v-app-bar flat :border="'b'" :class="isDark ? 'bg-surface' : 'bg-white'">
      <v-app-bar-nav-icon class="d-flex d-md-none" @click="mobileDrawer = true" />
      <v-app-bar-title>
        <span class="text-h6 font-weight-bold">{{ props.title }}</span>
      </v-app-bar-title>
      <template #append>
        <v-btn
          :icon="isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
          variant="text"
          class="mr-1"
          @click="toggleTheme"
        />
      </template>
    </v-app-bar>

    <v-navigation-drawer
      v-model="mobileDrawer"
      temporary
      :class="isDark ? 'sidebar-dark' : 'sidebar-light'"
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
          :active="props.active === item.value"
          active-color="error"
          rounded="lg"
          class="mb-1"
          @click="navigate(item)"
        />
      </v-list>
      <template #append>
        <v-divider />
        <v-menu location="top end" transition="scale-transition">
          <template #activator="{ props: menuProps }">
            <v-list-item
              v-bind="menuProps"
              :title="currentUser.name"
              :subtitle="currentUser.turma"
              nav
              class="profile-trigger py-3"
            >
              <template #prepend>
                <v-avatar color="error" size="34">
                  <span class="text-caption font-weight-bold text-white">{{ userInitials }}</span>
                </v-avatar>
              </template>
            </v-list-item>
          </template>

          <v-list class="profile-menu" density="compact" min-width="210">
            <v-list-item
              v-for="item in profileMenuItems"
              :key="item.title"
              :prepend-icon="item.icon"
              :title="item.title"
              @click="item.action"
            />
          </v-list>
        </v-menu>
      </template>
    </v-navigation-drawer>

    <v-main>
      <v-container fluid class="professor-page pa-4 pa-md-6">
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

<style>
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

.profile-trigger {
  cursor: pointer;
}

.profile-trigger :deep(.v-list-item-title) {
  font-weight: 600;
}

.profile-menu {
  border: 1px solid rgba(127, 127, 127, 0.22);
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.18);
}

.profile-menu-header {
  pointer-events: none;
}

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

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.9fr) minmax(280px, 0.7fr);
  gap: 18px;
  align-items: start;
  max-width: 1440px;
  margin: 0 auto;
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

.theme-dark .professor-page {
  background: #121214;
  color: #f0eeee;
}

.theme-dark .compact-hero,
.theme-dark .panel,
.theme-dark .preview-card,
.theme-dark .recent-card,
.theme-dark .profile-menu {
  background: #1d1d20;
  border-color: #333336;
  box-shadow: none;
}

.theme-dark .hero h1,
.theme-dark .section-heading h2,
.theme-dark .recent-heading h2,
.theme-dark .preview-card h3,
.theme-dark .history-item h3 {
  color: #f5f2ef;
}

.theme-dark .hero p:not(.eyebrow),
.theme-dark .section-heading p,
.theme-dark .preview-label > span,
.theme-dark .history-topline > span {
  color: #aaa4a0;
}

.theme-dark .selection-summary,
.theme-dark .command-card,
.theme-dark .loading-card {
  background: #252528;
  color: #d2cfcc;
}

.theme-dark .selection-summary strong {
  color: #f5f2ef;
}

.theme-dark .preview-card > p,
.theme-dark .preview-meta,
.theme-dark .history-item p,
.theme-dark .history-item time,
.theme-dark .support-text,
.theme-dark .command-card span {
  color: #bbb5b1;
}

.theme-dark .preview-meta,
.theme-dark .history-item {
  border-color: #333336;
}

.theme-dark .v-field,
.theme-dark .v-list,
.theme-dark .v-overlay__content > .v-card,
.theme-dark .v-overlay__content > .v-list {
  background-color: #1f1f22;
  color: #f5f2ef;
}

.theme-dark .v-field__outline,
.theme-dark .v-divider {
  color: #3a3a3d;
  border-color: #3a3a3d;
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
  .side-column {
    grid-template-columns: 1fr;
  }
}
</style>
