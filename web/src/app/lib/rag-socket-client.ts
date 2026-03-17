import type { RAGServerEvent, RAGTransport, TransportCallbacks } from '../types/rag';
import { log } from './logger';

interface CreateWebSocketTransportOptions {
  url: string;
}

interface SubmitQueryMessage {
  type: 'submit_query';
  query: string;
}

const isServerEvent = (value: unknown): value is RAGServerEvent => {
  if (!value || typeof value !== 'object' || !('type' in value)) {
    return false;
  }

  return typeof (value as { type?: unknown }).type === 'string';
};

export function createWebSocketTransport({
  url,
}: CreateWebSocketTransportOptions): RAGTransport {
  let socket: WebSocket | null = null;
  let callbacks: TransportCallbacks | null = null;

  const sendConnectionStatus = (status: Parameters<TransportCallbacks['onConnectionStatusChange']>[0]) => {
    callbacks?.onConnectionStatusChange(status);
  };

  const closeSocket = () => {
    if (!socket) {
      return;
    }

    socket.onopen = null;
    socket.onclose = null;
    socket.onerror = null;
    socket.onmessage = null;
    socket.close();
    socket = null;
  };

  return {
    mode: 'websocket',
    connect(nextCallbacks) {
      callbacks = nextCallbacks;
      sendConnectionStatus('connecting');

      try {
        socket = new WebSocket(url);
      } catch (error) {
        log('error', 'Failed to create WebSocket connection', { url });
        sendConnectionStatus('error');
        callbacks.onTransportError(error instanceof Error ? error.message : 'Failed to create WebSocket connection.');
        return;
      }

      socket.onopen = () => {
        log('info', 'WebSocket connected', { url });
        sendConnectionStatus('connected');
      };

      socket.onclose = () => {
        log('warn', 'WebSocket disconnected', { url });
        sendConnectionStatus('disconnected');
      };

      socket.onerror = () => {
        log('error', 'WebSocket connection error', { url });
        sendConnectionStatus('error');
        callbacks?.onTransportError('WebSocket connection error.');
      };

      socket.onmessage = (message) => {
        try {
          const payload = JSON.parse(message.data) as unknown;
          if (!isServerEvent(payload)) {
            callbacks?.onTransportError('Received an invalid server event.');
            return;
          }

          callbacks?.onEvent(payload);
        } catch (error) {
          callbacks?.onTransportError(error instanceof Error ? error.message : 'Failed to parse server event.');
        }
      };
    },
    disconnect() {
      closeSocket();
      callbacks = null;
    },
    submitQuery(query) {
      if (!socket || socket.readyState !== WebSocket.OPEN) {
        log('warn', 'Attempted to submit a query before WebSocket connection was open');
        callbacks?.onTransportError('WebSocket is not connected.');
        return;
      }

      const payload: SubmitQueryMessage = {
        type: 'submit_query',
        query,
      };
      log('info', 'Submitting websocket query', { query });
      socket.send(JSON.stringify(payload));
    },
  };
}
