import { useEffect, useState } from "react";
import { MarkdownAnswer } from "./markdown-answer";
import { appConfig } from "../lib/app-config";

interface TypewriterTextProps {
  text: string;
  isActive?: boolean;
  onProgress?: (displayedLength: number) => void;
  onDisplayComplete?: () => void;
}

export function TypewriterText({
  text,
  isActive = true,
  onProgress,
  onDisplayComplete,
}: TypewriterTextProps) {
  const [displayedText, setDisplayedText] = useState(text);
  const charsPerTick = Math.max(1, appConfig.typewriterCharsPerTick);
  const intervalMs = Math.max(16, appConfig.typewriterIntervalMs);

  useEffect(() => {
    if (!isActive) {
      setDisplayedText(text);
      return;
    }

    setDisplayedText((current) => {
      if (text.startsWith(current)) {
        return current;
      }
      return text;
    });
  }, [text, isActive]);

  useEffect(() => {
    onProgress?.(displayedText.length);
  }, [displayedText, onProgress]);

  useEffect(() => {
    if (displayedText.length === text.length && text.length > 0) {
      onDisplayComplete?.();
    }
  }, [displayedText.length, onDisplayComplete, text.length]);

  useEffect(() => {
    if (displayedText.length >= text.length) {
      return;
    }

    const timeout = window.setTimeout(() => {
      setDisplayedText(text.slice(0, displayedText.length + charsPerTick));
    }, intervalMs);

    return () => window.clearTimeout(timeout);
  }, [charsPerTick, displayedText, intervalMs, isActive, text]);

  return (
    <div className="relative">
      {isActive ? (
        <div className="whitespace-pre-wrap break-words text-gray-100">{displayedText}</div>
      ) : (
        <MarkdownAnswer markdown={text} />
      )}
      {isActive && (
        <span className="inline-block w-0.5 h-5 ml-0.5 bg-blue-400 align-middle animate-pulse" />
      )}
    </div>
  );
}
