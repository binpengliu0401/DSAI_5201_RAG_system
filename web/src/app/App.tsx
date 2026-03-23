import { useEffect, useState } from 'react';
import { QueryInput } from './components/query-input';
import { AnswerCard } from './components/answer-card';
import { ReasoningPanel } from './components/reasoning-panel';
import { LoadingSteps } from './components/loading-steps';
import { Card } from './components/ui/card';
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
  const showLoadingCard = isRunning && !!snapshot.currentStep;
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
    <div className="h-screen bg-[#0B0F14] overflow-hidden flex flex-col">
      {/* Background gradient effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      <div className="w-full mx-auto px-6 py-8 max-w-[1680px] relative z-10 flex-1 min-h-0 flex flex-col">
        <div className="absolute left-6 top-6 z-20">
          <div className={`inline-flex items-center gap-3 rounded-full border px-4 py-2 text-sm backdrop-blur-sm shadow-lg ${readinessClasses}`}>
            <span className={`relative flex size-2.5`}>
              <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 ${readinessDotClasses} ${isTransportReady ? 'animate-ping' : 'animate-pulse'}`} />
              <span className={`relative inline-flex size-2.5 rounded-full ${readinessDotClasses}`} />
            </span>
            <span>{readinessLabel}</span>
          </div>
        </div>

        {showReworkBeacon && reworkSignal && (
          <div className="absolute right-6 top-6 z-20">
            <div className="inline-flex items-center gap-3 rounded-full border border-amber-400/30 bg-amber-500/10 px-4 py-2 text-sm text-amber-200 backdrop-blur-sm shadow-lg shadow-amber-500/10">
              <span className="relative flex size-2.5">
                <span className="absolute inline-flex h-full w-full rounded-full bg-amber-300 opacity-50 animate-pulse" />
                <span className="relative inline-flex size-2.5 rounded-full bg-amber-300" />
              </span>
              <span>
                Reworking answer
                {reworkSignal.score !== undefined && reworkSignal.threshold !== undefined
                  ? ` (${reworkSignal.score.toFixed(2)} < ${reworkSignal.threshold.toFixed(2)})`
                  : ''}
              </span>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="mb-8 text-center flex-shrink-0 space-y-4">
          <div className="flex items-center justify-center gap-3 mb-3">
            <Brain className="size-8 text-blue-400" />
            <h1 className="text-4xl text-white">Neural Observatory</h1>
          </div>
          <p className="text-gray-400">Retrieval-Augmented Generation with Transparency</p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.7fr)_minmax(360px,0.9fr)] gap-8 flex-1 min-h-0 xl:overflow-hidden">
          {/* Left Column - Output and Loading */}
          <div className="space-y-4 min-h-0 xl:overflow-y-auto xl:pr-4 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
            {/* Loading State */}
            {showLoadingCard && snapshot.currentStep && (
              <Card className="p-3 bg-transparent border-0 shadow-none">
                <LoadingSteps currentStep={snapshot.currentStep} />
              </Card>
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
              <Card className="p-6 bg-red-500/10 border-red-500/30 backdrop-blur-sm">
                <div className="flex items-center gap-3 text-red-400">
                  <AlertCircle className="size-5" />
                  <p>{errorMessage}</p>
                </div>
              </Card>
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
        <div className="flex-shrink-0 bg-gradient-to-t from-[#0B0F14] via-[#0B0F14] to-transparent pt-6 pb-5">
          <div className="w-full max-w-5xl mx-auto">
            <div className="p-4 bg-gray-900/30 rounded-2xl backdrop-blur-xl border border-gray-800/80 shadow-2xl shadow-black/20">
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
    </div>
  );
}
