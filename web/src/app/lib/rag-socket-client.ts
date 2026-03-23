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
  let reconnectTimer: number | null = null;
  let manuallyDisconnected = false;

  const sendConnectionStatus = (status: Parameters<TransportCallbacks['onConnectionStatusChange']>[0]) => {
    callbacks?.onConnectionStatusChange(status);
  };

  const clearReconnectTimer = () => {
    if (reconnectTimer !== null) {
      window.clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
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

  const scheduleReconnect = () => {
    if (manuallyDisconnected || reconnectTimer !== null || !callbacks) {
      return;
    }

    sendConnectionStatus('connecting');
    reconnectTimer = window.setTimeout(() => {
      reconnectTimer = null;
      connectSocket();
    }, 1200);
  };

  const connectSocket = () => {
    clearReconnectTimer();

    try {
      socket = new WebSocket(url);
    } catch (error) {
      log('error', 'Failed to create WebSocket connection', { url });
      sendConnectionStatus('connecting');
      callbacks?.onTransportError(
        error instanceof Error ? error.message : 'Waiting for backend warmup.',
      );
      scheduleReconnect();
      return;
    }

    socket.onopen = () => {
      log('info', 'WebSocket connected', { url });
      sendConnectionStatus('connected');
    };

    socket.onclose = () => {
      log('warn', 'WebSocket disconnected', { url });
      if (manuallyDisconnected) {
        sendConnectionStatus('disconnected');
        return;
      }
      scheduleReconnect();
    };

    socket.onerror = () => {
      log('error', 'WebSocket connection error', { url });
      callbacks?.onTransportError('Waiting for backend warmup.');
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
  };

  return {
    mode: 'websocket',
    connect(nextCallbacks) {
      callbacks = nextCallbacks;
      manuallyDisconnected = false;
      sendConnectionStatus('connecting');
      connectSocket();
    },
    disconnect() {
      manuallyDisconnected = true;
      clearReconnectTimer();
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
