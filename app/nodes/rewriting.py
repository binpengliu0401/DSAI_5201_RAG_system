# ============================================================
# Owner:        Member C (Chen)
# Responsibility: Query Rewriting Node (Node 1)
# Status:       Stub — awaiting implementation by Member C
# ============================================================
#
# YOUR TASK:
#   Implement the rewrite_query() function below.
#
# INPUT  (read from state):
#   - state["query"]          str   original user question
#   - state["failed_queries"] list  queries already tried (empty on first run)
#                                   use this on retry to avoid repeating same rewrite
#
# OUTPUT (return as dict):
#   - "rewritten_query"  str        the improved query for retrieval
#   - "failed_queries"   list[str]  append the NEW rewritten query to this list
#   - "execution_trace"  list[dict] append one trace entry (see format below)
#
# TRACE FORMAT (append exactly one entry per call):
#   {
#       "node": "rewriting",
#       "status": "success",          # or "error"
#       "latency_ms": 123,
#       "summary": "Rewrote query: ...",
#       "key_output": {
#           "rewritten_query": "..."
#       }
#   }
#
# IMPORTANT:
#   - Do NOT raise exceptions — write to state["error_message"] and return
#   - Do NOT modify state directly — always return a dict
#   - "failed_queries" uses Annotated[list, operator.add] — just return a
#     list with the new query, LangGraph will auto-append it
#
# ============================================================

from app.graph.state import GraphState
from app.utils.tracer import build_trace_entry
import time


def rewrite_query(state: GraphState) -> dict:
    """
    Node 1: Query Rewriting
    Rewrites the user query to improve retrieval quality.
    On retry, uses failed_queries to avoid repeating previous attempts.
    """
    # TODO: implement by Member C
    # Stub: pass through original query unchanged
    start = time.time()

    rewritten = state["query"]  # replace this with real rewrite logic

    latency = round((time.time() - start) * 1000, 2)

    return {
        "rewritten_query": rewritten,
        "failed_queries": [rewritten],
        "execution_trace": [build_trace_entry(
            node="rewriting",
            status="success",
            latency_ms=latency,
            summary=f"[STUB] Passed through original query",
            key_output={"rewritten_query": rewritten}
        )]
    }