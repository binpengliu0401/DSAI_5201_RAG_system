import { Loader2 } from "lucide-react";

interface LoadingStepsProps {
  currentStep: 'rewriting' | 'retrieval' | 'generation' | 'grading' | 'complete';
}

const stepLabels: Record<string, string> = {
  rewriting: 'Rewriting query',
  retrieval: 'Retrieving documents',
  generation: 'Generating answer',
  grading: 'Checking confidence',
};

export function LoadingSteps({ currentStep }: LoadingStepsProps) {
  if (currentStep === 'complete') return null;
  const label = stepLabels[currentStep] ?? currentStep;

  return (
    <span className="inline-flex items-center gap-1.5 text-xs text-blue-400 font-mono">
      <Loader2 className="size-3 animate-spin flex-shrink-0" />
      {label}
    </span>
  );
}
