/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_ENV: string
  readonly VITE_FRONTEND_PUBLIC_URL: string
  readonly VITE_BACKEND_PUBLIC_URL: string
  readonly VITE_RAG_WS_URL: string
  readonly VITE_RAG_TRANSPORT_MODE: 'websocket' | 'demo' | 'auto'
  readonly VITE_RAG_ENGINE_MODE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
