import { useEffect, useState } from 'react';
import { QueryInput } from './components/query-input';
import { AnswerCard } from './components/answer-card';
import { ReasoningPanel } from './components/reasoning-panel';
import { LoadingSteps } from './components/loading-steps';
import { AlertCircle, Brain } from 'lucide-react';
import { useRAGSession } from './hooks/use-rag-session';
import { appConfig } from './lib/app-config';

export default function App() {
  const [query, setQuery] = useState('');
  const [showReworkBeacon, setShowReworkBeacon] = useState(false);
  const { snapshot, connectionStatus, transportMode, isRunning, submitQuery } = useRAGSession();
  const currentAttempt = snapshot.attempts.find((attempt) => attempt.attempt === snapshot.currentAttempt)
    ?? snapshot.attempts[snapshot.attempts.length - 1];
  const currentAnswer = currentAttempt?.answer ?? '';
  const isAnswerGenerating = currentAttempt?.answerStatus === 'streaming';

  const handleSubmit = async () => {
    if (!query.trim()) return;
    submitQuery(query);
  };

  const isTransportReady = connectionStatus === 'connected' || connectionStatus === 'demo';
  const shouldDisableInput = isRunning || !isTransportReady;
  const showAnswerCard = snapshot.runStatus !== 'idle' || currentAnswer.length > 0 || connectionStatus === 'connected' || connectionStatus === 'connecting';
  const shouldShowError = snapshot.runStatus === 'error' || connectionStatus === 'error' || connectionStatus === 'disconnected';
  const errorMessage = snapshot.error
    ?? (connectionStatus === 'disconnected' ? 'Connection lost. Reconnect the WebSocket to continue.' : '')
    ?? (connectionStatus === 'error' ? 'WebSocket connection error.' : '');
  const readinessLabel = transportMode === 'demo'
    ? 'Demo ready'
    : connectionStatus === 'connected'
    ? 'Backend ready'
    : connectionStatus === 'connecting'
    ? 'Waiting for backend warmup'
    : 'Backend unavailable';
  const readinessClasses = transportMode === 'demo'
    ? 'border-blue-500/30 bg-blue-500/10 text-blue-300'
    : connectionStatus === 'connected'
    ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
    : connectionStatus === 'connecting'
    ? 'border-yellow-500/30 bg-yellow-500/10 text-yellow-300'
    : 'border-red-500/30 bg-red-500/10 text-red-300';
  const readinessDotClasses = transportMode === 'demo'
    ? 'bg-blue-400'
    : connectionStatus === 'connected'
    ? 'bg-emerald-400'
    : connectionStatus === 'connecting'
    ? 'bg-yellow-400'
    : 'bg-red-400';
  const reworkSignal = snapshot.reworkSignal;

  useEffect(() => {
    if (!reworkSignal) {
      return;
    }

    setShowReworkBeacon(true);
    const timeout = window.setTimeout(() => {
      setShowReworkBeacon(false);
    }, appConfig.reworkBeaconDurationMs);

    return () => window.clearTimeout(timeout);
  }, [reworkSignal?.sequence]);

  return (
    <div className="h-screen gradient-bg-animated overflow-hidden flex flex-col">
      <div className="w-full mx-auto px-6 py-4 max-w-[1680px] relative z-10 flex-1 min-h-0 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between gap-4 py-3 mb-6 flex-shrink-0 border-b border-gray-800/60">
          <div className="flex items-center gap-3 min-w-0">
            <Brain className="size-5 text-blue-400 flex-shrink-0" />
            <h1 className="text-lg font-medium text-white">MathMind RAG</h1>
            {snapshot.currentStep && snapshot.currentStep !== 'complete' && (
              <LoadingSteps currentStep={snapshot.currentStep} />
            )}
          </div>
          <div className={`inline-flex items-center gap-2 rounded border px-3 py-1.5 text-xs font-mono flex-shrink-0 ${readinessClasses}`}>
            <span className="relative flex size-2">
              <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 ${readinessDotClasses} ${isTransportReady ? 'animate-ping' : 'animate-pulse'}`} />
              <span className={`relative inline-flex size-2 rounded-full ${readinessDotClasses}`} />
            </span>
            <span>{readinessLabel}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.7fr)_minmax(360px,0.9fr)] gap-8 flex-1 min-h-0 xl:overflow-hidden pb-2">
          {/* Left Column - Output and Loading */}
          <div className="flex flex-col gap-4 min-h-0 xl:pr-4 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
            {/* Rework Banner */}
            {showReworkBeacon && reworkSignal && (
              <div className="flex items-center gap-3 border-l-2 border-amber-500 bg-amber-500/5 px-4 py-2.5 text-sm text-amber-300">
                <span className="text-xs font-mono text-amber-500 flex-shrink-0">REWORK</span>
                <span className="font-mono text-xs">
                  {reworkSignal.score !== undefined && reworkSignal.threshold !== undefined
                    ? `score ${reworkSignal.score.toFixed(2)} < threshold ${reworkSignal.threshold.toFixed(2)}`
                    : 'reworking answer'}
                </span>
              </div>
            )}

            {/* Answer Display */}
            {showAnswerCard && (
              <AnswerCard
                answer={currentAnswer}
                hallucinationScore={currentAttempt?.hallucinationResult?.score}
                isGenerating={isAnswerGenerating}
                isComplete={currentAttempt?.answerStatus === 'complete'}
              />
            )}

            {/* Error State */}
            {shouldShowError && errorMessage && (
              <div className="flex items-center gap-3 border-l-2 border-red-700 bg-red-500/5 px-4 py-3 text-sm text-red-400">
                <AlertCircle className="size-4 flex-shrink-0" />
                <p className="font-mono text-xs">{errorMessage}</p>
              </div>
            )}
          </div>

          {/* Right Column - Reasoning Panel */}
          <div className="xl:col-span-1 min-h-0 xl:overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
            <ReasoningPanel
              snapshot={snapshot}
              connectionStatus={connectionStatus}
              transportMode={transportMode}
            />
          </div>
        </div>

        {/* Input Section */}
        <div className="flex-shrink-0 border-t border-gray-800 pt-4 pb-5">
          <div className="w-full max-w-5xl mx-auto">
            <QueryInput
              query={query}
              onQueryChange={setQuery}
              onSubmit={handleSubmit}
              isLoading={shouldDisableInput}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
