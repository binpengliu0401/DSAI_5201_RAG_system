import time
from langchain_core.documents import Document

from app.utils.tracer import build_trace_entry


def create_retrieval_node(retriever):
    def retrieval_node(state: dict) -> dict:
        start = time.time()

        rewritten_query = state["rewritten_query"]

        docs: list[Document] = retriever.retrieve(rewritten_query, top_k=5)

        latency = round((time.time() - start) * 1000, 2)

        return {
            "retrieved_docs": docs,
            "execution_trace": [
                build_trace_entry(
                    node="retrieval",
                    status="success",
                    latency_ms=latency,
                    summary=f"Retrieved {len(docs)} documents for rewritten query",
                    key_output={
                        "docs_retrieved": len(docs),
                        "query_preview": rewritten_query[:100],
                    },
                )
            ],
        }

    return retrieval_node
