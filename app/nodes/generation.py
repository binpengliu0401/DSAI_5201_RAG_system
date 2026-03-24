# Owner: Liu
# Responsibility: Generation Node — Node 3
# Input:  rewritten_query, retrieved_docs
# Output: answer, execution_trace

import re
import time

from langchain_core.prompts import ChatPromptTemplate

from app.graph.state import GraphState
from app.services.llm_service import get_llm
from app.utils.tracer import build_trace_entry
from config.logging import get_logger

logger = get_logger(__name__)

# prompt
GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Answer the user's question in a clear, teaching-oriented way using the provided information.

            Prioritize:
            1. Accuracy and grounding in the provided information
            2. Building intuition
            3. Clarity and readability

            Start with a simple 1-2 sentence explanation of the concept.

            Then explain how it works in a way that builds intuition. Include a short, concrete example if it helps understanding.

            IMPORTANT:
            - Do NOT include source markers like [Doc X]
            - Do NOT reference document numbers or retrieval artifacts
            - Do NOT mention "documents", "context", "sources", or citations in the answer
            - Do NOT explain where the information came from

            Instead, integrate the grounded information naturally into the explanation.

            Structure the answer for readability:
            - Use short paragraphs
            - Use bullet points only when they improve clarity
            - Highlight key concepts using **bold** sparingly

            Maintain a professional and approachable tone: not overly casual, not academic, not report-like.

            Be concise, but do not omit important explanations.
            Avoid repetition and unnecessary jargon.

            If the available information is insufficient, say so clearly and briefly.

            Information:
{context}""",
        ),
        ("human", "{question}"),
    ]
)


# Helper
def format_docs(docs) -> str:
    return "\n\n".join(str(doc.page_content).strip() for doc in docs)


def clean_answer_text(answer: str) -> str:
    cleaned = re.sub(r"\[Doc\s*\d+\]", "", answer, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    return cleaned.strip()


# Node
def generate_answer(state: GraphState) -> dict:
    start = time.time()
    try:
        rewritten_query = state["rewritten_query"]
        retrieved_docs = state["retrieved_docs"]

        context = format_docs(retrieved_docs)
        llm = get_llm("generation")

        # LCEL
        chain = GENERATION_PROMPT | llm

        response = chain.invoke({"context": context, "question": rewritten_query})

        answer = clean_answer_text(str(response.content))
        contains_source_markers = bool(
            re.search(r"\[Doc\s*\d+\]", answer, flags=re.IGNORECASE)
        )
        logger.info(
            "Generated answer chars=%d contains_source_markers=%s",
            len(answer),
            contains_source_markers,
        )
        latency = round((time.time() - start) * 1000, 2)

        return {
            "answer": answer,
            "execution_trace": [
                build_trace_entry(
                    node="generation",
                    status="success",
                    latency_ms=latency,
                    summary=f"Generated answer from {len(retrieved_docs)} retrieved docs",
                    key_output={
                        "answer_preview": answer[:100] + "..." if len(answer) > 100 else answer,  # type: ignore
                        "doc_count": len(retrieved_docs),
                    },
                )
            ],
        }
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        return {
            "answer": "",
            "error_message": f"Generation failed: {str(e)}",
            "execution_trace": [
                build_trace_entry(
                    node="generation",
                    status="error",
                    latency_ms=latency,
                    summary=f"Generation failed: {str(e)}",
                    key_output={},
                )
            ],
        }
