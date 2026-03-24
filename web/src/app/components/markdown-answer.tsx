import { memo } from "react";
import type { ReactNode } from "react";

interface MarkdownAnswerProps {
  markdown: string;
}

interface ParsedParagraph {
  kind: "paragraph";
  text: string;
}

interface ParsedHeading {
  kind: "heading";
  level: 1 | 2 | 3;
  text: string;
}

interface ParsedList {
  kind: "list";
  items: string[];
}

type ParsedBlock = ParsedParagraph | ParsedHeading | ParsedList;

export const MarkdownAnswer = memo(function MarkdownAnswer({ markdown }: MarkdownAnswerProps) {
  const blocks = parseMarkdown(markdown);

  return (
    <div className="space-y-3">
      {blocks.map((block, index) => {
        if (block.kind === "heading") {
          const className =
            block.level === 1
              ? "text-xl font-semibold text-white"
              : block.level === 2
              ? "text-lg font-semibold text-white"
              : "text-base font-semibold text-white";

          return (
            <div key={index} className={className}>
              {renderInline(block.text)}
            </div>
          );
        }

        if (block.kind === "list") {
          return (
            <ul key={index} className="list-disc pl-5 space-y-1 text-gray-100">
              {block.items.map((item, itemIndex) => (
                <li key={itemIndex}>{renderInline(item)}</li>
              ))}
            </ul>
          );
        }

        return (
          <p key={index} className="text-gray-100">
            {renderInline(block.text)}
          </p>
        );
      })}
    </div>
  );
});

function parseMarkdown(markdown: string): ParsedBlock[] {
  const normalized = markdown.replace(/\r\n/g, "\n").trim();
  if (!normalized) {
    return [];
  }

  const lines = normalized.split("\n");
  const blocks: ParsedBlock[] = [];
  let paragraphLines: string[] = [];
  let listItems: string[] = [];

  const flushParagraph = () => {
    const text = paragraphLines.join(" ").trim();
    if (text) {
      blocks.push({ kind: "paragraph", text });
    }
    paragraphLines = [];
  };

  const flushList = () => {
    if (listItems.length > 0) {
      blocks.push({ kind: "list", items: listItems });
    }
    listItems = [];
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (!line) {
      flushParagraph();
      flushList();
      continue;
    }

    const headingMatch = line.match(/^(#{1,3})\s+(.*)$/);
    if (headingMatch) {
      flushParagraph();
      flushList();
      blocks.push({
        kind: "heading",
        level: headingMatch[1].length as 1 | 2 | 3,
        text: headingMatch[2].trim(),
      });
      continue;
    }

    const listMatch = line.match(/^[-*]\s+(.*)$/);
    if (listMatch) {
      flushParagraph();
      listItems.push(listMatch[1].trim());
      continue;
    }

    flushList();
    paragraphLines.push(line);
  }

  flushParagraph();
  flushList();
  return blocks;
}

function renderInline(text: string): ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
  return parts.map((part, index) => {
    const match = part.match(/^\*\*([^*]+)\*\*$/);
    if (match) {
      return (
        <strong key={index} className="font-semibold text-white">
          {match[1]}
        </strong>
      );
    }
    return <span key={index}>{part}</span>;
  });
}
