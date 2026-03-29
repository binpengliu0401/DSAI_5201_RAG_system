import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { AlertCircle, CheckCircle2, AlertTriangle } from "lucide-react";
import { TypewriterText } from "./typewriter-text";
import { useEffect, useRef, useState } from "react";

interface AnswerCardProps {
  answer: string;
  hallucinationScore?: number;
  isGenerating?: boolean;
  isComplete?: boolean;
}

export function AnswerCard({
  answer,
  hallucinationScore,
  isGenerating = false,
  isComplete = false,
}: AnswerCardProps) {
  const [displayComplete, setDisplayComplete] = useState(false);
  const [displayedLength, setDisplayedLength] = useState(0);
  const bodyScrollRef = useRef<HTMLDivElement | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const shouldFollowTailRef = useRef(true);

  useEffect(() => {
    if (answer.length === 0) {
      setDisplayComplete(false);
      return;
    }

    if (displayedLength < answer.length) {
      setDisplayComplete(false);
      return;
    }

    if (!isGenerating) {
      setDisplayComplete(true);
    }
  }, [answer.length, displayedLength, isGenerating]);

  useEffect(() => {
    if (answer.length === 0) {
      setDisplayedLength(0);
      setDisplayComplete(false);
    }
  }, [answer.length]);

  useEffect(() => {
    if (isGenerating) {
      setDisplayComplete(false);
    }
  }, [isGenerating]);

  useEffect(() => {
    const container = bodyScrollRef.current;
    if (!container) {
      return;
    }

    const updateFollowState = () => {
      const distanceFromBottom =
        container.scrollHeight - container.scrollTop - container.clientHeight;
      shouldFollowTailRef.current = distanceFromBottom < 120;
    };

    updateFollowState();
    container.addEventListener('scroll', updateFollowState, { passive: true });
    return () => container.removeEventListener('scroll', updateFollowState);
  }, []);

  useEffect(() => {
    if (!isGenerating || !bodyScrollRef.current || !bottomRef.current) {
      return;
    }

    if (shouldFollowTailRef.current) {
      const container = bodyScrollRef.current;
      window.requestAnimationFrame(() => {
        container.scrollTop = container.scrollHeight;
      });
    }
  }, [displayedLength, isGenerating]);

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'green';
    if (score >= 0.4) return 'yellow';
    return 'red';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 0.7) return <CheckCircle2 className="size-4" />;
    if (score >= 0.4) return <AlertTriangle className="size-4" />;
    return <AlertCircle className="size-4" />;
  };

  const getScoreLabel = (score: number) => {
    if (score >= 0.7) return 'Grounded';
    if (score >= 0.4) return 'Partially Grounded';
    return 'Low Confidence';
  };

  const scoreColor = hallucinationScore ? getScoreColor(hallucinationScore) : 'green';
  const scoreColorClasses = {
    green: 'bg-transparent text-green-400 border-green-800',
    yellow: 'bg-transparent text-yellow-400 border-yellow-800',
    red: 'bg-transparent text-red-400 border-red-800'
  };

  return (
    <Card className="flex-1 min-h-0 flex flex-col gap-4 p-6 bg-[#0e1217] border-gray-800">
      <div className="flex items-center justify-between gap-4">
        <span className="text-xs uppercase tracking-widest font-mono text-gray-500">Answer</span>
        {isComplete && (
          <span className="text-xs font-mono text-green-600">✓ complete</span>
        )}
      </div>

      {isGenerating && (
        <div className="text-xs font-mono text-blue-400 animate-pulse">// generating...</div>
      )}
      
      <div
        ref={bodyScrollRef}
        className="text-gray-100 leading-relaxed text-base flex-1 min-h-0 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent"
      >
        {answer.length > 0 ? (
          <>
            <TypewriterText 
              text={answer} 
              isActive={isGenerating || !displayComplete}
              onProgress={setDisplayedLength}
              onDisplayComplete={() => {
                if (!displayComplete) {
                  setDisplayComplete(true);
                }
              }}
            />
            <div ref={bottomRef} />
          </>
        ) : (
          <div className="text-xs font-mono text-gray-600">
            {isGenerating ? '// waiting for tokens...' : '// ask a question to begin'}
          </div>
        )}
      </div>

      {hallucinationScore !== undefined && displayComplete && (
        <div className="flex items-center gap-3 pt-3 border-t border-gray-800 animate-in fade-in duration-500">
          <Badge
            variant="outline"
            className={`inline-flex items-center gap-1.5 ${scoreColorClasses[scoreColor]}`}
          >
            {getScoreIcon(hallucinationScore)}
            <span>{getScoreLabel(hallucinationScore)}</span>
            <span className="font-mono opacity-70">{hallucinationScore.toFixed(2)}</span>
          </Badge>
        </div>
      )}
    </Card>
  );
}
