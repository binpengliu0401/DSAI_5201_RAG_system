import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Sparkles } from "lucide-react";

interface QueryInputProps {
  query: string;
  onQueryChange: (query: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

export function QueryInput({ query, onQueryChange, onSubmit, isLoading }: QueryInputProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (query.trim() && !isLoading) {
        onSubmit();
      }
    }
  };

  return (
    <div className="w-full">
      <label className="text-xs uppercase tracking-widest font-mono text-gray-500 mb-2 block">
        Query
      </label>
      <div className="flex gap-3 items-start">
        <Textarea
          placeholder="e.g., What are the main benefits of retrieval-augmented generation?"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 min-h-[52px] max-h-[84px] resize-none bg-[#0e1217] border-gray-800 text-gray-100 placeholder:text-gray-600 focus:border-gray-600 focus:ring-0 transition-colors text-sm"
          disabled={isLoading}
        />
        <Button
          onClick={onSubmit}
          disabled={!query.trim() || isLoading}
          className="h-[52px] px-7 bg-blue-700 hover:bg-blue-600 text-white border-0 transition-colors disabled:opacity-30 flex-shrink-0 font-mono text-sm rounded"
        >
          {isLoading ? (
            <>
              <Sparkles className="size-4 mr-2 animate-pulse" />
              running
            </>
          ) : (
            'run'
          )}
        </Button>
      </div>
    </div>
  );
}
