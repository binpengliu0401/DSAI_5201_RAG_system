# ============================================================
# Owner:        Member B (Li)
# Responsibility: Retrieval Node (Node 2)
# Status:       Stub — awaiting implementation by Member B
# ============================================================
#
# YOUR TASK:
#   Implement the retrieve_docs() function below.
#   You are also responsible for building and loading the FAISS index.
#   The index path is configured in .env as FAISS_INDEX_PATH.
#
# INPUT  (read from state):
#   - state["rewritten_query"]  str  query after rewriting (from Node 1)
#
# OUTPUT (return as dict):
#   - "retrieved_docs"   List[Document]  retrieved chunks
#   - "execution_trace"  list[dict]      append one trace entry
#
# CRITICAL TYPE REQUIREMENT:
#   retrieved_docs MUST be List[Document] from langchain_core.documents
#   Do NOT return raw strings or dicts — the Generation node depends on this type
#
#   Example:
#     from langchain_core.documents import Document
#     doc = Document(page_content="...", metadata={"source": "paper.pdf"})
#
# TRACE FORMAT:
#   {
#       "node": "retrieval",
#       "status": "success",
#       "latency_ms": 45,
#       "summary": "Retrieved 5 chunks",
#       "key_output": {
#           "doc_count": 5,
#           "sources": ["paper1.pdf", ...]
#       }
#   }
#
# IMPORTANT:
#   - Do NOT raise exceptions — write to state["error_message"] and return
#   - FAISS index loading should happen outside this function (e.g. at startup)
#     and be passed in or imported as a module-level variable
#
# ============================================================

from app.graph.state import GraphState
from app.utils.tracer import build_trace_entry
from langchain_core.documents import Document
import time


def retrieve_docs(state: GraphState) -> dict:
    """
    Node 2: Retrieval
    Retrieves relevant document chunks from FAISS vector store.
    """
    # TODO: implement by Member B
    # Stub: return one fake document so the graph can run end-to-end
    start = time.time()

    fake_docs = [
        Document(
            page_content="[STUB] This is a placeholder document for testing.",
            metadata={"source": "stub"}
        )
    ]

    latency = round((time.time() - start) * 1000, 2)

    return {
        "retrieved_docs": fake_docs,
        "execution_trace": [build_trace_entry(
            node="retrieval",
            status="success",
            latency_ms=latency,
            summary=f"[STUB] Returned 1 placeholder document",
            key_output={"doc_count": 1, "sources": ["stub"]}
        )]
    }