import { createDemoTransport } from './rag-demo-client';
import { createWebSocketTransport } from './rag-socket-client';
import type { RAGTransport } from '../types/rag';
import { appConfig } from './app-config';
import { log } from './logger';

export function createRAGTransport(): RAGTransport {
  const wsUrl = appConfig.ragWsUrl;
  const transportMode = appConfig.transportMode;

  if (transportMode !== 'demo' && typeof wsUrl === 'string' && wsUrl.trim().length > 0) {
    log('info', 'Using WebSocket transport', {
      backendPublicUrl: appConfig.backendPublicUrl,
      ragWsUrl: wsUrl,
      ragEngineMode: appConfig.ragEngineMode,
    });
    return createWebSocketTransport({ url: wsUrl });
  }

  log('warn', 'Falling back to demo transport', {
    backendPublicUrl: appConfig.backendPublicUrl,
    configuredWsUrl: wsUrl,
    transportMode,
  });
  return createDemoTransport();
}
