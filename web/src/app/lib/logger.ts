import { appConfig } from './app-config';

type Level = 'info' | 'warn' | 'error';

export function log(level: Level, message: string, context?: Record<string, unknown>) {
  const payload = context ? { ...context, appEnv: appConfig.appEnv } : { appEnv: appConfig.appEnv };
  const prefix = '[rag-web]';

  if (level === 'warn') {
    console.warn(prefix, message, payload);
    return;
  }

  if (level === 'error') {
    console.error(prefix, message, payload);
    return;
  }

  console.info(prefix, message, payload);
}
