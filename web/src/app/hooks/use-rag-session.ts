import { useEffect, useMemo, useReducer, useRef } from 'react';
import { createRAGTransport } from '../lib/create-rag-transport';
import {
  type AttemptSnapshot,
  createEmptySnapshot,
  type ConnectionStatus,
  type RAGServerEvent,
  type RAGTransport,
  type SessionSnapshot,
  type SessionState,
} from '../types/rag';

type SessionAction =
  | { type: 'connection_status_changed'; status: ConnectionStatus }
  | { type: 'transport_error'; message: string }
  | { type: 'submit_requested'; query: string }
  | { type: 'server_event_received'; event: RAGServerEvent };

const initialState: SessionState = {
  connectionStatus: 'connecting',
  transportMode: 'demo',
  snapshot: createEmptySnapshot(),
};

const WARMUP_MESSAGE = 'Waiting for backend warmup.';
let reworkSequence = 0;

function createEmptyAttempt(attempt: number): AttemptSnapshot {
  return {
    attempt,
    rewrittenQuery: '',
    retrievedDocs: [],
    answer: '',
    answerStatus: 'idle',
    status: 'running',
    hallucinationResult: undefined,
  };
}

function upsertAttempt(
  snapshot: SessionSnapshot,
  attempt: number,
  updater?: (current: AttemptSnapshot) => AttemptSnapshot,
): SessionSnapshot {
  const existing = snapshot.attempts.find((entry) => entry.attempt === attempt);
  const current = existing ?? createEmptyAttempt(attempt);
  const nextAttempt = updater ? updater(current) : current;
  const attempts = existing
    ? snapshot.attempts.map((entry) => (entry.attempt === attempt ? nextAttempt : entry))
    : [...snapshot.attempts, nextAttempt].sort((a, b) => a.attempt - b.attempt);

  return {
    ...snapshot,
    currentAttempt: attempt,
    attempts,
  };
}

function applyServerEvent(snapshot: SessionSnapshot, event: RAGServerEvent): SessionSnapshot {
  switch (event.type) {
    case 'run_started':
      return {
        ...createEmptySnapshot(),
        runId: event.runId,
        query: event.query,
        runStatus: 'running',
        currentStep: 'rewriting',
      };
    case 'attempt_started':
      return upsertAttempt(snapshot, event.attempt);
    case 'stage_started':
      return {
        ...snapshot,
        currentAttempt: event.attempt,
        currentStep: event.stage,
        runStatus: 'running',
      };
    case 'stage_completed':
      return snapshot;
    case 'step_changed':
      return {
        ...snapshot,
        currentStep: event.step,
        currentAttempt: event.attempt,
        runStatus: event.step === 'complete' ? 'complete' : 'running',
      };
    case 'query_rewritten':
      return upsertAttempt(snapshot, event.attempt, (attempt) => ({
        ...attempt,
        rewrittenQuery: event.rewrittenQuery,
        retrievedDocs: [],
        answer: '',
        answerStatus: 'idle',
        hallucinationResult: undefined,
      }));
    case 'documents_retrieved':
      return upsertAttempt(snapshot, event.attempt, (attempt) => ({
        ...attempt,
        retrievedDocs: event.retrievedDocs,
      }));
    case 'answer_delta':
      return upsertAttempt(snapshot, event.attempt, (attempt) => ({
        ...attempt,
        answer: `${attempt.answer}${event.delta}`,
        answerStatus: 'streaming',
      }));
    case 'answer_replaced':
      return upsertAttempt(snapshot, event.attempt, (attempt) => ({
        ...attempt,
        answer: event.answer,
        answerStatus: event.answer.length > 0 ? 'streaming' : 'idle',
      }));
    case 'answer_completed':
      return upsertAttempt(snapshot, event.attempt, (attempt) => ({
        ...attempt,
        answerStatus: 'complete',
      }));
    case 'attempt_rework_triggered':
      return {
        ...upsertAttempt(snapshot, event.attempt, (attempt) => ({
          ...attempt,
          status: 'reworked',
        })),
        reworkSignal: {
          attempt: event.attempt,
          reason: event.reason,
          score: event.score,
          threshold: event.threshold,
          sequence: ++reworkSequence,
        },
      };
    case 'grading_completed':
      return upsertAttempt(snapshot, event.attempt, (attempt) => ({
        ...attempt,
        hallucinationResult: event.hallucinationResult,
      }));
    case 'attempt_completed':
      return upsertAttempt(snapshot, event.attempt, (attempt) => ({
        ...attempt,
        status: event.outcome,
      }));
    case 'run_completed':
      return {
        ...snapshot,
        runStatus: 'complete',
        currentStep: 'complete',
      };
    case 'run_failed':
      return {
        ...snapshot,
        runStatus: 'error',
        error: event.error,
      };
    case 'snapshot':
      return {
        ...snapshot,
        ...event.snapshot,
      };
    default:
      return snapshot;
  }
}

function sessionReducer(state: SessionState, action: SessionAction): SessionState {
  switch (action.type) {
    case 'connection_status_changed':
      return {
        ...state,
        connectionStatus: action.status,
      };
    case 'transport_error':
      if (action.message === WARMUP_MESSAGE) {
        return {
          ...state,
          snapshot: {
            ...state.snapshot,
            error: undefined,
          },
        };
      }
      return {
        ...state,
        snapshot: {
          ...state.snapshot,
          runStatus: state.snapshot.runStatus === 'idle' ? 'idle' : 'error',
          error: action.message,
        },
      };
    case 'submit_requested':
      return {
        ...state,
        snapshot: {
          ...createEmptySnapshot(),
          query: action.query,
          runStatus: 'running',
          currentStep: 'rewriting',
        },
      };
    case 'server_event_received':
      return {
        ...state,
        snapshot: applyServerEvent(state.snapshot, action.event),
      };
    default:
      return state;
  }
}

export function useRAGSession() {
  const [state, dispatch] = useReducer(sessionReducer, initialState);
  const transportRef = useRef<RAGTransport | null>(null);
  const transport = useMemo(() => createRAGTransport(), []);

  useEffect(() => {
    transportRef.current = transport;

    dispatch({
      type: 'connection_status_changed',
      status: transport.mode === 'demo' ? 'demo' : 'connecting',
    });

    transport.connect({
      onConnectionStatusChange: (status) => {
        dispatch({ type: 'connection_status_changed', status });
      },
      onEvent: (event) => {
        dispatch({ type: 'server_event_received', event });
      },
      onTransportError: (message) => {
        dispatch({ type: 'transport_error', message });
      },
    });

    return () => {
      transport.disconnect();
      transportRef.current = null;
    };
  }, [transport]);

  const submitQuery = (query: string) => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      return;
    }

    dispatch({ type: 'submit_requested', query: trimmedQuery });
    transportRef.current?.submitQuery(trimmedQuery);
  };

  return {
    connectionStatus: state.connectionStatus,
    transportMode: transport.mode,
    snapshot: state.snapshot,
    isRunning: state.snapshot.runStatus === 'running',
    submitQuery,
  };
}
