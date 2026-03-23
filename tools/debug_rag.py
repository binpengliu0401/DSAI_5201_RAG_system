import argparse
import sys
from pathlib import Path
from pprint import pprint

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.utils.tracer import print_trace
from main import run_workflow


def _print_stage_outputs(state: dict) -> None:
    print("Stage outputs")
    print(f"  Rewrite: {state.get('rewritten_query')}")
    print(f"  Answer: {state.get('answer')}")
    print(f"  Hallucination score: {state.get('hallucination_score')}")
    print(f"  Final decision: {state.get('final_decision')}")

    docs = state.get("retrieved_docs", []) or []
    print(f"  Retrieved docs: {len(docs)}")
    for index, doc in enumerate(docs, start=1):
        metadata = getattr(doc, "metadata", {}) or {}
        source = metadata.get("source") or metadata.get("title") or f"Document {index}"
        content = str(getattr(doc, "page_content", "")).strip()
        preview = content[:300] + ("..." if len(content) > 300 else "")
        print(f"\n  [Doc {index}] source={source}")
        print(f"  {preview}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manual RAG debug entrypoint")
    parser.add_argument("query", nargs="?", default="What is vision transformer")
    parser.add_argument(
        "--show-state",
        action="store_true",
        help="Pretty-print the final workflow state",
    )
    args = parser.parse_args()

    state = run_workflow(args.query)

    print_trace(state)
    _print_stage_outputs(state)

    if args.show_state:
        print("\nFinal state")
        pprint(state)


if __name__ == "__main__":
    main()
