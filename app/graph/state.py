# Owner: Liu
# Responsibility: GraphState schema — shared contract for all nodes

import operator
from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from langchain_core.documents import Document


class GraphState(TypedDict):
    query: str
    rewritten_query: str
    failed_queries: Annotated[list, operator.add]
    retrieved_docs: List[Document]
    answer: str
    hallucination_score: float
    retry_count: int
    max_retries: int
    final_decision: str
    error_message: Optional[str]
    execution_trace: Annotated[list, operator.add]