import { defineConfig, loadEnv } from 'vite'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

const toNumber = (value: string | undefined, fallback: number) => {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

const buildUrl = (protocol: string, host: string, port: number, pathName = '') => {
  const normalizedPath = pathName ? (pathName.startsWith('/') ? pathName : `/${pathName}`) : ''
  return `${protocol}://${host}:${port}${normalizedPath}`
}

export default defineConfig(({ mode }) => {
  const rootEnvDir = path.resolve(__dirname, '..')
  const env = loadEnv(mode, rootEnvDir, '')

  const frontendProtocol = env.FRONTEND_PROTOCOL || 'http'
  const frontendHost = env.FRONTEND_HOST || '127.0.0.1'
  const frontendPort = toNumber(env.FRONTEND_PORT, 5173)
  const backendProtocol = env.BACKEND_PROTOCOL || 'http'
  const backendWsProtocol = env.BACKEND_WS_PROTOCOL || 'ws'
  const backendPublicHost =
    env.BACKEND_PUBLIC_HOST ||
    (env.BACKEND_HOST === '0.0.0.0' ? '127.0.0.1' : (env.BACKEND_HOST || '127.0.0.1'))
  const backendPort = toNumber(env.BACKEND_PORT, 8000)
  const backendPublicUrl = env.BACKEND_PUBLIC_URL || buildUrl(
    backendProtocol,
    backendPublicHost,
    backendPort,
    env.BACKEND_API_PREFIX || '',
  )
  const backendWsUrl = env.BACKEND_WS_URL || buildUrl(
    backendWsProtocol,
    backendPublicHost,
    backendPort,
    env.BACKEND_WS_PATH || '/ws/rag',
  )

  return {
    envDir: rootEnvDir,
    plugins: [
      react(),
      tailwindcss(),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      host: frontendHost,
      port: frontendPort,
    },
    preview: {
      host: frontendHost,
      port: frontendPort,
    },
    define: {
      'import.meta.env.VITE_APP_ENV': JSON.stringify(env.APP_ENV || 'development'),
      'import.meta.env.VITE_FRONTEND_PUBLIC_URL': JSON.stringify(
        env.FRONTEND_PUBLIC_URL || buildUrl(frontendProtocol, frontendHost, frontendPort),
      ),
      'import.meta.env.VITE_BACKEND_PUBLIC_URL': JSON.stringify(backendPublicUrl),
      'import.meta.env.VITE_RAG_WS_URL': JSON.stringify(backendWsUrl),
      'import.meta.env.VITE_RAG_TRANSPORT_MODE': JSON.stringify(env.FRONTEND_RAG_TRANSPORT || 'websocket'),
      'import.meta.env.VITE_RAG_ENGINE_MODE': JSON.stringify(env.RAG_ENGINE_MODE || 'fake'),
    },
    assetsInclude: ['**/*.svg', '**/*.csv'],
  }
})
