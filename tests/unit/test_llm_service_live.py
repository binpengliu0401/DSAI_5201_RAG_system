from pydantic import BaseModel
import pytest

from app.services.llm_service import get_llm
from app.utils.constants import LLM_API_KEY


pytestmark = pytest.mark.skipif(
    not LLM_API_KEY,
    reason="LLM_API_KEY is not configured for live LLM smoke tests.",
)


class RagSummary(BaseModel):
    term: str
    benefit: str


def test_live_get_llm_invoke_returns_non_empty_content():
    llm = get_llm()

    response = llm.invoke(
        "What is Retrieval-Augmented Generation? Answer in one short paragraph."
    )

    assert isinstance(response.content, str)
    assert response.content.strip()


def test_live_get_llm_structured_output_returns_expected_fields():
    llm = get_llm().with_structured_output(RagSummary)

    response = llm.invoke(
        'Describe RAG as JSON with fields "term" and "benefit".'
    )

    assert isinstance(response, RagSummary)
    assert response.term.strip()
    assert response.benefit.strip()


def test_live_get_llm_stream_returns_content_chunks():
    llm = get_llm()

    chunks = list(llm.stream("Explain RAG in one or two short sentences."))

    assert chunks
    assert any(getattr(chunk, "content", "").strip() for chunk in chunks)
