# Owner: Liu
# Responsibility: LangGraph assembly — connects all nodes into a complete graph

from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.router import route_decision, get_next_node
from app.nodes.rewriting import rewrite_query
from app.services.retriever import RAGRetriever
from app.nodes.retrieval import create_retrieval_node
from app.nodes.generation import generate_answer
from app.nodes.grading import grade_hallucination
from app.utils.constants import MAX_RETRIES
from config.logging import get_logger

logger = get_logger(__name__)


def create_retriever() -> RAGRetriever:
    retriever = RAGRetriever(
        parquet_path="data/train-00000-of-00001.parquet", index_dir="data/index"
    )
    try:
        retriever.load()
        logger.info("Retriever index loaded from disk")
    except FileNotFoundError:
        logger.warning("Retriever index missing; building index before serving queries")
        retriever.build()
        retriever.load()
        logger.info("Retriever index built and loaded")
    return retriever


def build_graph():
    retriever = create_retriever()
    retieval_node = create_retrieval_node(retriever)

    # Initialize graph with state schema
    graph = StateGraph(GraphState)

    # Register nodes
    graph.add_node("rewriting", rewrite_query)
    graph.add_node("retrieval", retieval_node)  # type: ignore
    graph.add_node("generation", generate_answer)
    graph.add_node("grading", grade_hallucination)
    graph.add_node("router", route_decision)

    # Define edges
    graph.set_entry_point("rewriting")
    graph.add_edge("rewriting", "retrieval")
    graph.add_edge("retrieval", "generation")
    graph.add_edge("generation", "grading")
    graph.add_edge("grading", "router")

    # Conditonal edge from router
    graph.add_conditional_edges(
        "router", get_next_node, {"rewriting": "rewriting", "output": END}
    )

    return graph.compile()


rag_graph = build_graph()
