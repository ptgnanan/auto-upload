import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './styles/index.scss'
import { setRuntimeBackendPort } from './utils/api-runtime'

async function bootstrapRuntimeBackendPort() {
  if (import.meta.env.VITE_API_BASE_URL) return

  try {
    const response = await fetch('/api/runtime', { cache: 'no-store' })
    if (!response.ok) return

    const payload = await response.json()
    if (payload?.backendPort) {
      setRuntimeBackendPort(payload.backendPort)
    }
  } catch (error) {
    console.warn('Failed to resolve backend runtime port:', error)
  }
}

async function bootstrapApp() {
  await bootstrapRuntimeBackendPort()

  const app = createApp(App)

  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }

  app.use(router)
  app.use(pinia)
  app.use(ElementPlus)
  app.mount('#app')
}

bootstrapApp()
