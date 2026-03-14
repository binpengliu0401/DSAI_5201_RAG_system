# ============================================================
# Owner:        Member D (Hu)
# Responsibility: Hallucination Grading Node (Node 4)
# Status:       Stub — awaiting implementation by Member D
# ============================================================
#
# YOUR TASK:
#   Implement the grade_hallucination() function below.
#   This node judges whether the generated answer is grounded
#   in the retrieved documents.
#
# INPUT  (read from state):
#   - state["answer"]         str             generated answer from Node 3
#   - state["retrieved_docs"] List[Document]  source documents from Node 2
#
# OUTPUT (return as dict):
#   - "hallucination_score"  float       score from 0.0 to 1.0
#                                        >= 0.7 means acceptable (router will output)
#                                        <  0.7 means hallucination detected (router may retry)
#   - "execution_trace"      list[dict]  append one trace entry
#
# SCORE CONVENTION (IMPORTANT — router logic depends on this):
#   1.0 = perfectly grounded, no hallucination
#   0.0 = completely hallucinated, no support in docs
#   threshold = 0.7 (defined in app/utils/constants.py)
#
# TRACE FORMAT:
#   {
#       "node": "grading",
#       "status": "success",
#       "latency_ms": 28,
#       "summary": "Score: 0.83 — answer is grounded",
#       "key_output": {
#           "hallucination_score": 0.83
#       }
#   }
#
# IMPORTANT:
#   - Do NOT raise exceptions — write to state["error_message"] and return
#   - If grading fails, return score = 0.0 and write error to error_message
#
# ============================================================

from app.graph.state import GraphState
from app.utils.tracer import build_trace_entry
import time


def grade_hallucination(state: GraphState) -> dict:
    """
    Node 4: Hallucination Grading
    Evaluates whether the generated answer is supported by retrieved docs.
    """
    # TODO: implement by Member D
    # Stub: always return 0.5 to trigger at least one retry during testing
    start = time.time()

    score = 0.5  # replace with real grading logic

    latency = round((time.time() - start) * 1000, 2)

    return {
        "hallucination_score": score,
        "execution_trace": [build_trace_entry(
            node="grading",
            status="success",
            latency_ms=latency,
            summary=f"[STUB] Returning fixed score {score}",
            key_output={"hallucination_score": score}
        )]
    }