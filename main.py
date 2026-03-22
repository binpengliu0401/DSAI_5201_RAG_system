# Owner: Liu
# Responsibility: Local CLI entry point for development and demo

from app.graph.builder import rag_graph
from app.utils.tracer import print_trace
from app.utils.constants import MAX_RETRIES
from config.logging import configure_logging, get_logger
from config.settings import settings
from scripts.setup_data import ensure_data_ready


configure_logging(settings.runtime.log_level)
logger = get_logger(__name__)

ensure_data_ready()


# Initialize state and invoke the full RAG graph, return final state as dict
def run_workflow(query: str) -> dict:
    logger.info("Starting RAG workflow for query: %s", query)
    initial_state = {
        "query": query,
        "rewritten_query": "",
        "failed_queries": [],
        "retrieved_docs": [],
        "answer": "",
        "hallucination_score": 0.0,
        "retry_count": 0,
        "max_retries": MAX_RETRIES,
        "final_decision": "",
        "error_message": None,
        "execution_trace": [],
    }

    final_state = rag_graph.invoke(initial_state)  # type: ignore
    logger.info(
        "Workflow completed with decision=%s score=%.2f retries=%s",
        final_state.get("final_decision", ""),
        float(final_state.get("hallucination_score", 0.0)),
        final_state.get("retry_count", 0),
    )
    return final_state


if __name__ == "__main__":
    import sys

    query = sys.argv[1] if len(sys.argv) > 1 else "What is chain of thought prompting?"
    run_workflow(query)
