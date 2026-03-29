import { memo } from "react";
import { Card } from "./ui/card";
import { FileText, RefreshCw, FileSearch, MessageSquare, ShieldCheck } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { ChevronDown, CheckCircle2 } from "lucide-react";
import type { AttemptSnapshot, ConnectionStatus, SessionSnapshot, TransportMode } from "../types/rag";

interface ReasoningPanelProps {
  snapshot: SessionSnapshot;
  connectionStatus: ConnectionStatus;
  transportMode: TransportMode;
}

export const ReasoningPanel = memo(function ReasoningPanel({
  snapshot,
  connectionStatus,
  transportMode,
}: ReasoningPanelProps) {
  const currentAttempt = snapshot.attempts.find((attempt) => attempt.attempt === snapshot.currentAttempt)
    ?? snapshot.attempts[snapshot.attempts.length - 1];

  if (
    !snapshot.query &&
    snapshot.attempts.length === 0
  ) {
    return (
      <Card className="p-6 bg-[#0e1217] border-gray-800 h-full">
        <div className="mb-6">
          <h3 className="text-xs uppercase tracking-widest font-mono text-gray-500">Reasoning Trace</h3>
        </div>
        <div className="text-center py-12">
          <FileText className="size-8 mx-auto mb-3 text-gray-700" />
          <p className="text-xs font-mono text-gray-600">// awaiting query</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6 bg-[#0e1217] border-gray-800 h-full flex flex-col">
      <div className="mb-6 flex-shrink-0">
        <h3 className="text-xs uppercase tracking-widest font-mono text-gray-500">Reasoning Trace</h3>
      </div>

      <div className="space-y-8 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
        <TraceBody snapshot={snapshot} currentAttempt={currentAttempt} />
      </div>
    </Card>
  );
}, areReasoningPanelPropsEqual);

function TraceBody({
  snapshot,
  currentAttempt,
}: {
  snapshot: SessionSnapshot;
  currentAttempt?: AttemptSnapshot;
}) {
  const currentStep = snapshot.currentStep;
  const previousAttempts = currentAttempt
    ? snapshot.attempts.filter((attempt) => attempt.attempt !== currentAttempt.attempt)
    : snapshot.attempts;

  const getStepStatus = (step: string) => {
    if (!currentStep) return 'pending';
    const steps = ['rewriting', 'retrieval', 'generation', 'grading', 'complete'];
    const currentIndex = steps.indexOf(currentStep);
    const stepIndex = steps.indexOf(step);

    if (currentStep === 'complete' || stepIndex < currentIndex) return 'complete';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="space-y-6 relative">
      {/* Retry History */}
      {snapshot.attempts.length > 1 && (
        <div className="border border-gray-800 bg-[#0a0d11] p-4 space-y-3 rounded-lg">
          <div className="flex items-center justify-between gap-3">
            <span className="text-xs uppercase tracking-widest font-mono text-gray-500">Retry History</span>
            <span className="text-xs font-mono text-gray-600">{snapshot.attempts.length} attempts</span>
          </div>
          <div className="space-y-2">
            {previousAttempts.map((attempt) => (
              <Collapsible key={attempt.attempt}>
                <CollapsibleTrigger className="w-full">
                  <div className="flex items-start justify-between gap-3 rounded border border-gray-800 bg-[#0a0d11] p-3 text-left hover:border-gray-700 transition-colors">
                    <div className="space-y-0.5 min-w-0">
                      <div className="text-xs font-mono text-gray-400">attempt_{attempt.attempt}</div>
                      <div className="text-xs font-mono text-gray-600 truncate">
                        {attempt.rewrittenQuery || '—'}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {attempt.hallucinationResult && (
                        <span className="text-xs font-mono text-gray-500">
                          {attempt.hallucinationResult.score.toFixed(2)}
                        </span>
                      )}
                      <ChevronDown className="size-4 text-gray-600 group-data-[state=open]:rotate-180 transition-transform" />
                    </div>
                  </div>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <div className="mt-1 rounded border border-gray-800 bg-[#0a0d11] p-3 space-y-3">
                    <div>
                      <div className="text-xs uppercase tracking-wide font-mono text-gray-600 mb-1">rewrite</div>
                      <div className="text-xs font-mono text-gray-400">{attempt.rewrittenQuery || '—'}</div>
                    </div>
                    <div>
                      <div className="text-xs uppercase tracking-wide font-mono text-gray-600 mb-1">answer</div>
                      <div className="text-sm text-gray-400 whitespace-pre-wrap">
                        {attempt.answer || '—'}
                      </div>
                    </div>
                    {attempt.hallucinationResult && (
                      <div>
                        <div className="text-xs uppercase tracking-wide font-mono text-gray-600 mb-1">score</div>
                        <div className="text-xs font-mono text-gray-400">
                          {attempt.hallucinationResult.score.toFixed(2)} — {attempt.hallucinationResult.explanation}
                        </div>
                      </div>
                    )}
                  </div>
                </CollapsibleContent>
              </Collapsible>
            ))}
          </div>
        </div>
      )}

      {!currentAttempt ? (
        <div className="text-xs font-mono text-gray-600 py-2">// waiting for first attempt</div>
      ) : (
        <>
          <div className="flex items-center justify-between gap-3">
            <span className="text-xs uppercase tracking-widest font-mono text-gray-500">
              Attempt <span className="text-gray-300">{currentAttempt.attempt}</span>
            </span>
            <span className="text-xs font-mono text-blue-400">active</span>
          </div>

          {/* Timeline line */}
          <div className="absolute left-[19px] top-6 bottom-0 w-px bg-gray-800" />

          {/* Rewritten Query */}
          <div className="relative">
            <div className="flex items-start gap-4">
              <div className={`size-10 rounded flex items-center justify-center z-10 flex-shrink-0 ${
                getStepStatus('rewriting') === 'complete'
                  ? 'bg-green-900/30 border border-green-800 text-green-500'
                  : getStepStatus('rewriting') === 'active'
                  ? 'bg-blue-900/30 border border-blue-800 text-blue-400'
                  : 'bg-gray-900 border border-gray-800 text-gray-700'
              }`}>
                <RefreshCw className="size-4" />
              </div>
              <div className="flex-1 space-y-2 pt-1 min-w-0">
                <div className="text-xs uppercase tracking-wide font-mono text-gray-500">Query Rewrite</div>
                {getStepStatus('rewriting') !== 'pending' && (
                  <div className="bg-[#0a0d11] rounded p-3 text-xs font-mono text-gray-300 border border-gray-800">
                    {currentAttempt.rewrittenQuery || '// waiting...'}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Retrieved Documents */}
          <div className="relative">
            <div className="flex items-start gap-4">
              <div className={`size-10 rounded flex items-center justify-center z-10 flex-shrink-0 ${
                getStepStatus('retrieval') === 'complete'
                  ? 'bg-green-900/30 border border-green-800 text-green-500'
                  : getStepStatus('retrieval') === 'active'
                  ? 'bg-blue-900/30 border border-blue-800 text-blue-400'
                  : 'bg-gray-900 border border-gray-800 text-gray-700'
              }`}>
                <FileSearch className="size-4" />
              </div>
              <div className="flex-1 space-y-2 pt-1 min-w-0">
                <div className="text-xs uppercase tracking-wide font-mono text-gray-500">Retrieved Documents</div>
                {getStepStatus('retrieval') !== 'pending' && (
                  <div className="space-y-1.5">
                    {currentAttempt.retrievedDocs.length === 0 && (
                      <div className="text-xs font-mono text-gray-600 py-1">// waiting for context</div>
                    )}
                    {currentAttempt.retrievedDocs.map((doc, idx) => (
                      <Collapsible key={doc.id}>
                        <CollapsibleTrigger className="w-full">
                          <div className="flex items-start gap-2 bg-[#0a0d11] rounded p-2.5 border border-gray-800 hover:border-gray-700 transition-colors cursor-pointer group">
                            <ChevronDown className="size-3.5 text-gray-600 mt-0.5 group-data-[state=open]:rotate-180 transition-transform flex-shrink-0" />
                            <div className="flex-1 text-left min-w-0">
                              <div className="flex items-center justify-between gap-2 mb-0.5">
                                <div className="flex items-center gap-2 min-w-0">
                                  <span className="text-xs font-mono text-gray-600 flex-shrink-0">
                                    [{String(idx + 1).padStart(2, '0')}]
                                  </span>
                                  <span className="text-xs text-gray-400 truncate">{doc.source}</span>
                                </div>
                                <div className="flex items-center gap-2 flex-shrink-0">
                                  {doc.relevant && (
                                    <CheckCircle2 className="size-3 text-green-600" />
                                  )}
                                  {doc.score !== undefined && (
                                    <span className="text-xs font-mono text-gray-600">{doc.score.toFixed(2)}</span>
                                  )}
                                </div>
                              </div>
                              <p className="text-xs text-gray-600 line-clamp-1">{doc.snippet}</p>
                            </div>
                          </div>
                        </CollapsibleTrigger>
                        <CollapsibleContent>
                          <div className="ml-5 mt-1 p-2.5 bg-[#0a0d11] rounded border border-gray-800 text-xs text-gray-500 font-mono leading-relaxed">
                            {doc.snippet}
                          </div>
                        </CollapsibleContent>
                      </Collapsible>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Generation */}
          <div className="relative">
            <div className="flex items-start gap-4">
              <div className={`size-10 rounded flex items-center justify-center z-10 flex-shrink-0 ${
                getStepStatus('generation') === 'complete'
                  ? 'bg-green-900/30 border border-green-800 text-green-500'
                  : getStepStatus('generation') === 'active'
                  ? 'bg-blue-900/30 border border-blue-800 text-blue-400'
                  : 'bg-gray-900 border border-gray-800 text-gray-700'
              }`}>
                <MessageSquare className="size-4" />
              </div>
              <div className="flex-1 space-y-2 pt-1">
                <div className="text-xs uppercase tracking-wide font-mono text-gray-500">Generation</div>
                {getStepStatus('generation') === 'active' && (
                  <div className="text-xs font-mono text-blue-400 animate-pulse">// generating response</div>
                )}
                {getStepStatus('generation') === 'complete' && (
                  <div className="text-xs font-mono text-green-600">// stream complete</div>
                )}
              </div>
            </div>
          </div>

          {/* Hallucination Detection */}
          <div className="relative">
            <div className="flex items-start gap-4">
              <div className={`size-10 rounded flex items-center justify-center z-10 flex-shrink-0 ${
                getStepStatus('grading') === 'complete'
                  ? (currentAttempt.hallucinationResult?.score ?? 0) >= 0.7
                    ? 'bg-green-900/30 border border-green-800 text-green-500'
                    : (currentAttempt.hallucinationResult?.score ?? 0) >= 0.4
                    ? 'bg-yellow-900/30 border border-yellow-800 text-yellow-500'
                    : 'bg-red-900/30 border border-red-800 text-red-500'
                  : getStepStatus('grading') === 'active'
                  ? 'bg-blue-900/30 border border-blue-800 text-blue-400'
                  : 'bg-gray-900 border border-gray-800 text-gray-700'
              }`}>
                <ShieldCheck className="size-4" />
              </div>
              <div className="flex-1 space-y-2 pt-1">
                <div className="text-xs uppercase tracking-wide font-mono text-gray-500">Hallucination Detection</div>

                {getStepStatus('grading') !== 'pending' && (
                  <div className="space-y-2">
                    {!currentAttempt.hallucinationResult && (
                      <div className="text-xs font-mono text-gray-600">// waiting for assessment</div>
                    )}
                    {currentAttempt.hallucinationResult && (
                      <>
                        <div className="flex items-center justify-between bg-[#0a0d11] rounded p-3 border border-gray-800">
                          <span className="text-xs uppercase tracking-wide font-mono text-gray-500">Confidence</span>
                          <span className={`text-sm font-mono font-medium ${
                            currentAttempt.hallucinationResult.score >= 0.7 ? 'text-green-400' :
                            currentAttempt.hallucinationResult.score >= 0.4 ? 'text-yellow-400' :
                            'text-red-400'
                          }`}>
                            {currentAttempt.hallucinationResult.score.toFixed(2)}
                          </span>
                        </div>

                        <div className="bg-[#0a0d11] rounded p-3 border border-gray-800">
                          <p className="text-xs text-gray-400 leading-relaxed">{currentAttempt.hallucinationResult.explanation}</p>
                        </div>

                        {currentAttempt.hallucinationResult.unsupportedClaims && currentAttempt.hallucinationResult.unsupportedClaims.length > 0 && (
                          <div className="border-l-2 border-red-800 bg-red-500/5 px-3 py-2.5 space-y-1">
                            <p className="text-xs uppercase tracking-wide font-mono text-red-600 mb-2">Unsupported Claims</p>
                            <ul className="space-y-1">
                              {currentAttempt.hallucinationResult.unsupportedClaims.map((claim, idx) => (
                                <li key={idx} className="text-xs text-red-400 font-mono">— {claim}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function areReasoningPanelPropsEqual(
  previous: ReasoningPanelProps,
  next: ReasoningPanelProps,
) {
  if (
    previous.connectionStatus !== next.connectionStatus ||
    previous.transportMode !== next.transportMode
  ) {
    return false;
  }

  const previousSnapshot = previous.snapshot;
  const nextSnapshot = next.snapshot;
  if (
    previousSnapshot.query !== nextSnapshot.query ||
    previousSnapshot.runStatus !== nextSnapshot.runStatus ||
    previousSnapshot.currentStep !== nextSnapshot.currentStep ||
    previousSnapshot.currentAttempt !== nextSnapshot.currentAttempt ||
    previousSnapshot.attempts.length !== nextSnapshot.attempts.length
  ) {
    return false;
  }

  return previousSnapshot.attempts.every((attempt, index) => {
    const nextAttempt = nextSnapshot.attempts[index];
    if (!nextAttempt) {
      return false;
    }

    // Ignore active-attempt answer deltas to keep the trace panel from rerendering on every chunk.
    const ignoreAnswerChange = attempt.attempt === nextSnapshot.currentAttempt;

    return (
      attempt.attempt === nextAttempt.attempt &&
      attempt.rewrittenQuery === nextAttempt.rewrittenQuery &&
      attempt.answerStatus === nextAttempt.answerStatus &&
      (ignoreAnswerChange || attempt.answer === nextAttempt.answer) &&
      attempt.hallucinationResult?.score === nextAttempt.hallucinationResult?.score &&
      attempt.hallucinationResult?.explanation === nextAttempt.hallucinationResult?.explanation &&
      attempt.retrievedDocs.length === nextAttempt.retrievedDocs.length &&
      attempt.retrievedDocs.every((doc, docIndex) => {
        const nextDoc = nextAttempt.retrievedDocs[docIndex];
        return !!nextDoc &&
          doc.id === nextDoc.id &&
          doc.title === nextDoc.title &&
          doc.snippet === nextDoc.snippet &&
          doc.score === nextDoc.score &&
          doc.relevant === nextDoc.relevant;
      })
    );
  });
}
