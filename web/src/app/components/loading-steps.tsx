import { CheckCircle2, FileSearch, Loader2, MessageSquare, RefreshCw, ShieldCheck } from "lucide-react";

interface LoadingStepsProps {
  currentStep: 'rewriting' | 'retrieval' | 'generation' | 'grading' | 'complete';
}

const steps = [
  { id: 'rewriting', label: 'Rewrite', icon: RefreshCw },
  { id: 'retrieval', label: 'Retrieve', icon: FileSearch },
  { id: 'generation', label: 'Generate', icon: MessageSquare },
  { id: 'grading', label: 'Confidence', icon: ShieldCheck },
] as const;

export function LoadingSteps({ currentStep }: LoadingStepsProps) {
  const currentIndex = steps.findIndex((step) => step.id === currentStep);

  return (
    <div className="rounded-2xl border border-gray-800 bg-gray-900/40 px-4 py-4 backdrop-blur-sm">
      <div className="flex items-center gap-3 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
        {steps.map((step, index) => {
          const isComplete = currentStep === 'complete' || index < currentIndex;
          const isCurrent = index === currentIndex;
          const Icon = step.icon;

          return (
            <div key={step.id} className="flex items-center gap-3 min-w-fit">
              <div className="flex items-center gap-3 rounded-full border border-gray-800 bg-gray-950/60 px-4 py-2">
                <div className={`flex size-8 items-center justify-center rounded-full border ${
                  isComplete
                    ? 'border-green-500 bg-green-500/20 text-green-400'
                    : isCurrent
                    ? 'border-blue-500 bg-blue-500/20 text-blue-400'
                    : 'border-gray-700 bg-gray-800/60 text-gray-500'
                }`}>
                  {isComplete ? (
                    <CheckCircle2 className="size-4" />
                  ) : isCurrent ? (
                    <Loader2 className="size-4 animate-spin" />
                  ) : (
                    <Icon className="size-4" />
                  )}
                </div>
                <div className="flex flex-col">
                  <span className={`text-sm font-medium ${
                    isComplete ? 'text-green-300' :
                    isCurrent ? 'text-blue-300' :
                    'text-gray-400'
                  }`}>
                    {step.label}
                  </span>
                  <span className="text-xs text-gray-500">
                    {isComplete ? 'Done' : isCurrent ? 'In progress' : 'Pending'}
                  </span>
                </div>
              </div>
              {index < steps.length - 1 && (
                <div className={`h-px w-8 ${
                  currentStep === 'complete' || index < currentIndex
                    ? 'bg-green-500/50'
                    : 'bg-gray-800'
                }`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
