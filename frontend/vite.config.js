import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import fs from 'fs'

const API_PREFIXES = [
  '/login',
  '/upload',
  '/uploadSave',
  '/getFiles',
  '/getFile',
  '/deleteFile',
  '/getAccounts',
  '/getValidAccounts',
  '/deleteAccount',
  '/postVideo',
  '/postVideoBatch',
  '/updateUserinfo',
  '/uploadCookie',
  '/downloadCookie',
  '/syncProfile',
  '/openCreatorCenter',
  '/checkAccount',
  '/api/v2',
]

const runtimeFile = resolve(__dirname, '../data/runtime.json')

const readBackendPort = () => {
  try {
    const content = fs.readFileSync(runtimeFile, 'utf-8')
    const payload = JSON.parse(content)
    const port = Number(payload?.backendPort)
    return Number.isInteger(port) && port > 0 ? port : 5409
  } catch {
    return 5409
  }
}

const createDynamicProxy = () => ({
  target: 'http://127.0.0.1:5409',
  changeOrigin: true,
  timeout: 120000,
  proxyTimeout: 120000,
  router: () => `http://127.0.0.1:${readBackendPort()}`,
})

const proxy = Object.fromEntries(API_PREFIXES.map((prefix) => [prefix, createDynamicProxy()]))

export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'runtime-port-endpoint',
      configureServer(server) {
        server.middlewares.use('/api/runtime', (_req, res) => {
          const payload = JSON.stringify({ backendPort: readBackendPort() })
          res.setHeader('Content-Type', 'application/json; charset=utf-8')
          res.setHeader('Cache-Control', 'no-store')
          res.end(payload)
        })
      },
    },
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {},
    },
  },
  server: {
    port: 5173,
    open: true,
    proxy,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 1600,
    rollupOptions: {
      output: {
        manualChunks: {
          vue: ['vue', 'vue-router', 'pinia'],
          elementPlus: ['element-plus'],
          utils: ['axios'],
        },
      },
    },
  },
})
