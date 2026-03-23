export type ProcessingStep = 'rewriting' | 'retrieval' | 'generation' | 'grading' | 'complete';
export type PipelineStage = 'rewriting' | 'retrieval' | 'generation' | 'grading';

export type RunStatus = 'idle' | 'running' | 'complete' | 'error';
export type AnswerStatus = 'idle' | 'streaming' | 'complete';

export type ConnectionStatus = 'connecting' | 'connected' | 'demo' | 'disconnected' | 'error';

export type TransportMode = 'websocket' | 'demo';

export interface RetrievedDoc {
  id: string;
  title: string;
  source: string;
  snippet: string;
  score?: number;
  relevant: boolean;
}

export interface HallucinationResult {
  score: number;
  explanation: string;
  unsupportedClaims?: string[];
}

export interface AttemptSnapshot {
  attempt: number;
  rewrittenQuery: string;
  retrievedDocs: RetrievedDoc[];
  answer: string;
  answerStatus: AnswerStatus;
  status: 'running' | 'completed' | 'reworked' | 'failed';
  hallucinationResult?: HallucinationResult;
}

export interface ReworkSignal {
  attempt: number;
  reason: string;
  score?: number;
  threshold?: number;
  sequence: number;
}

export interface SessionSnapshot {
  runId?: string;
  query: string;
  runStatus: RunStatus;
  currentStep?: ProcessingStep;
  currentAttempt?: number;
  attempts: AttemptSnapshot[];
  reworkSignal?: ReworkSignal;
  error?: string;
}

export interface SessionState {
  connectionStatus: ConnectionStatus;
  transportMode: TransportMode;
  snapshot: SessionSnapshot;
}

export type RAGServerEvent =
  | { type: 'run_started'; runId?: string; query: string }
  | { type: 'attempt_started'; attempt: number }
  | { type: 'stage_started'; attempt: number; stage: PipelineStage }
  | { type: 'stage_completed'; attempt: number; stage: PipelineStage }
  | { type: 'step_changed'; step: ProcessingStep; attempt: number }
  | { type: 'query_rewritten'; attempt: number; rewrittenQuery: string }
  | { type: 'documents_retrieved'; attempt: number; retrievedDocs: RetrievedDoc[] }
  | { type: 'answer_delta'; attempt: number; delta: string }
  | { type: 'answer_replaced'; attempt: number; answer: string }
  | { type: 'answer_completed'; attempt: number }
  | { type: 'attempt_rework_triggered'; attempt: number; reason: string; score?: number; threshold?: number }
  | { type: 'grading_completed'; attempt: number; hallucinationResult: HallucinationResult }
  | { type: 'attempt_completed'; attempt: number; outcome: 'completed' | 'reworked' | 'failed' }
  | { type: 'run_completed' }
  | { type: 'run_failed'; error: string }
  | { type: 'snapshot'; snapshot: Partial<SessionSnapshot> };

export interface TransportCallbacks {
  onConnectionStatusChange: (status: ConnectionStatus) => void;
  onEvent: (event: RAGServerEvent) => void;
  onTransportError: (message: string) => void;
}

export interface RAGTransport {
  mode: TransportMode;
  connect: (callbacks: TransportCallbacks) => void;
  disconnect: () => void;
  submitQuery: (query: string) => void;
}

export const createEmptySnapshot = (): SessionSnapshot => ({
  query: '',
  runStatus: 'idle',
  currentStep: undefined,
  currentAttempt: undefined,
  attempts: [],
  reworkSignal: undefined,
  error: undefined,
});
