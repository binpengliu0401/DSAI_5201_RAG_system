import time
from langchain_core.documents import Document


def create_retrieval_node(retriever):

    def retrieval_node(state: dict) -> dict:
        start = time.time()

        rewritten_query = state["rewritten_query"]

        docs: list[Document] = retriever.retrieve(rewritten_query, top_k=5)

        latency = round(time.time() - start, 2)

        return {
            "retrieved_docs": docs,  
            "execution_trace": [  
                {"node": "retrieval", "latency": latency, "docs_retrieved": len(docs)}
            ],
        }

    return retrieval_node
