import { computed, ref, watch } from 'vue'

type AppTheme = 'light' | 'dark'

const STORAGE_KEY = 'siga-theme'

function readStoredTheme(): AppTheme {
  if (typeof window === 'undefined') return 'light'
  return localStorage.getItem(STORAGE_KEY) === 'dark' ? 'dark' : 'light'
}

const theme = ref<AppTheme>(readStoredTheme())

if (typeof window !== 'undefined') {
  watch(
    theme,
    value => {
      localStorage.setItem(STORAGE_KEY, value)
      document.documentElement.dataset.theme = value
    },
    { immediate: true },
  )
}

export function useAppTheme() {
  const isDark = computed(() => theme.value === 'dark')

  function toggleTheme() {
    theme.value = isDark.value ? 'light' : 'dark'
  }

  function setTheme(value: AppTheme) {
    theme.value = value
  }

  return {
    theme,
    isDark,
    toggleTheme,
    setTheme,
  }
}
