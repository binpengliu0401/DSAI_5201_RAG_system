export interface AppConfig {
  appEnv: string;
  frontendPublicUrl: string;
  backendPublicUrl: string;
  ragWsUrl: string;
  transportMode: 'websocket' | 'demo' | 'auto';
  ragEngineMode: string;
  typewriterIntervalMs: number;
  typewriterCharsPerTick: number;
  reworkBeaconDurationMs: number;
}

export const appConfig: AppConfig = {
  appEnv: import.meta.env.VITE_APP_ENV,
  frontendPublicUrl: import.meta.env.VITE_FRONTEND_PUBLIC_URL,
  backendPublicUrl: import.meta.env.VITE_BACKEND_PUBLIC_URL,
  ragWsUrl: import.meta.env.VITE_RAG_WS_URL,
  transportMode: import.meta.env.VITE_RAG_TRANSPORT_MODE,
  ragEngineMode: import.meta.env.VITE_RAG_ENGINE_MODE,
  typewriterIntervalMs: import.meta.env.VITE_TYPEWRITER_INTERVAL_MS,
  typewriterCharsPerTick: import.meta.env.VITE_TYPEWRITER_CHARS_PER_TICK,
  reworkBeaconDurationMs: import.meta.env.VITE_REWORK_BEACON_DURATION_MS,
};
