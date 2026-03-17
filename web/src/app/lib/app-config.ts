export interface AppConfig {
  appEnv: string;
  frontendPublicUrl: string;
  backendPublicUrl: string;
  ragWsUrl: string;
  transportMode: 'websocket' | 'demo' | 'auto';
  ragEngineMode: string;
}

export const appConfig: AppConfig = {
  appEnv: import.meta.env.VITE_APP_ENV,
  frontendPublicUrl: import.meta.env.VITE_FRONTEND_PUBLIC_URL,
  backendPublicUrl: import.meta.env.VITE_BACKEND_PUBLIC_URL,
  ragWsUrl: import.meta.env.VITE_RAG_WS_URL,
  transportMode: import.meta.env.VITE_RAG_TRANSPORT_MODE,
  ragEngineMode: import.meta.env.VITE_RAG_ENGINE_MODE,
};
