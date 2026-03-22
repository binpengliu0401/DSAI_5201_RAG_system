from scripts.setup_data import ensure_data_ready
from app.graph.builder import rag_graph
from app.utils.tracer import print_trace


def run_workflow(query: str) -> dict:
    print(f"\n[main] Running workflow for query: {query}")

    ensure_data_ready()

    initial_state = {
        "query": query,
        "rewritten_query": "",
        "failed_queries": [],
        "retrieved_docs": [],
        "answer": "",
        "hallucination_score": 0.0,
        "retry_count": 0,
        "max_retries": 2,
        "final_decision": "",
        "error_message": None,
        "execution_trace": [],
    }

    final_state = rag_graph.invoke(initial_state)  # type: ignore

    print(f"\n[main] Decision: {final_state.get('final_decision')}")
    print(f"[main] Score: {final_state.get('hallucination_score'):.2f}")
    print(f"[main] Retries: {final_state.get('retry_count')}")
    print(f"\n[main] Answer:\n{final_state.get('answer')}")

    return final_state


def main():
    print("Hello from dsai-5201-rag-system!")


if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "What is chain of thought prompting?"
    run_workflow(query)
