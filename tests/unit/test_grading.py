# ============================================================
# Test for: Node 4 — Hallucination Grading
# Run:      python -m pytest tests/test_grading.py -v
# Owner:    Member D (Hu) — run this after your implementation
# ============================================================

from unittest.mock import patch

import pytest
from langchain_core.documents import Document

from app.nodes import grading
from app.nodes.grading import grade_hallucination


def make_state(answer: str, retrieved_docs: list, query: str = "What is RAG?") -> dict:  # type: ignore
    return {
        "query": query,
        "answer": answer,
        "retrieved_docs": retrieved_docs,
    }


def make_document(content: str) -> Document:  # type: ignore
    return Document(page_content=content, metadata={"source": "test_doc"})


def make_claim(claim: str, label: str) -> grading.ClaimAssessment:
    return grading.ClaimAssessment(claim=claim, label=label, explanation="")


@patch("app.nodes.grading._grade_answer")
def test_returns_required_keys(mock_grade_answer):
    mock_grade_answer.return_value = grading.GradingResult(
        score=1.0,
        verdict="grounded",
        explanation="All claims are grounded.",
        claim_count=2,
    )

    result = grade_hallucination(
        make_state(
            "RAG improves answer grounding.",
            [make_document("RAG uses retrieved documents to ground the answer.")],
        )
    )

    assert "hallucination_score" in result
    assert "execution_trace" in result


@patch("app.nodes.grading._grade_answer")
def test_score_is_float_between_0_and_1(mock_grade_answer):
    mock_grade_answer.return_value = grading.GradingResult(
        score=1.02,
        verdict="grounded",
        explanation="All claims are grounded.",
        claim_count=1,
    )

    result = grade_hallucination(
        make_state(
            "RAG improves answer grounding.",
            [make_document("RAG uses retrieved documents to ground the answer.")],
        )
    )

    assert isinstance(result["hallucination_score"], float)
    assert 0.0 <= result["hallucination_score"] <= 1.0
    assert result["hallucination_score"] == 1.0


@patch("app.nodes.grading._grade_answer")
def test_grounded_answer_scores_high(mock_grade_answer):
    mock_grade_answer.return_value = grading.GradingResult(
        claims=[
            make_claim("RAG combines retrieval and generation.", "supported"),
            make_claim("RAG improves factual grounding.", "supported"),
        ],
        verdict="grounded",
        explanation="All claims are supported.",
    )

    result = grade_hallucination(
        make_state(
            "RAG combines retrieval and generation. RAG improves factual grounding.",
            [make_document("RAG combines retrieval and generation and improves factual grounding.")],
        )
    )

    assert result["hallucination_score"] >= 0.7


@patch("app.nodes.grading._grade_answer")
def test_partial_answer_scores_midrange(mock_grade_answer):
    mock_grade_answer.return_value = grading.GradingResult(
        score=0.5,
        verdict="partially_grounded",
        explanation="One claim is supported and one is unsupported.",
        partial_claims=["RAG always lowers cost."],
        unsupported_claims=["RAG guarantees perfect correctness."],
        claim_count=2,
    )

    result = grade_hallucination(
        make_state(
            "RAG lowers cost and guarantees perfect correctness.",
            [make_document("RAG improves factual grounding and verifiability.")],
        )
    )

    assert 0.0 < result["hallucination_score"] < 0.7


@patch("app.nodes.grading._grade_answer")
def test_unsupported_answer_scores_low(mock_grade_answer):
    mock_grade_answer.return_value = grading.GradingResult(
        score=0.0,
        verdict="unsupported",
        explanation="No claims are supported.",
        unsupported_claims=[
            "RAG was invented in 2024.",
            "RAG eliminates retrieval entirely.",
        ],
        claim_count=2,
    )

    result = grade_hallucination(
        make_state(
            "RAG was invented in 2024 and eliminates retrieval entirely.",
            [make_document("RAG combines retrieval with generation.")],
        )
    )

    assert result["hallucination_score"] < 0.7


def test_aggregation_correctness():
    result = grading._normalize_result(
        grading.GradingResult(
            score=0.99,
            verdict="grounded",
            explanation="Test aggregation.",
            claims=[
                make_claim("Claim A", "supported"),
                make_claim("Claim B", "partial"),
                make_claim("Claim C", "unsupported"),
            ],
        )
    )

    assert result.claim_count == 3
    assert result.supported_claims == ["Claim A"]
    assert result.partial_claims == ["Claim B"]
    assert result.unsupported_claims == ["Claim C"]
    assert result.score == pytest.approx(0.5)
    assert result.verdict == "partially_grounded"


@patch("app.nodes.grading._grade_answer")
def test_trace_entry_format(mock_grade_answer):
    mock_grade_answer.return_value = grading.GradingResult(
        score=0.5,
        verdict="partially_grounded",
        explanation="One supported and one unsupported claim.",
        unsupported_claims=["Unsupported claim."],
        claim_count=2,
    )

    result = grade_hallucination(
        make_state(
            "RAG improves grounding but guarantees perfect accuracy.",
            [make_document("RAG improves grounding.")],
        )
    )

    trace = result["execution_trace"]
    assert isinstance(trace, list)
    assert len(trace) == 1

    entry = trace[0]
    assert entry["node"] == "grading"
    assert "status" in entry
    assert "latency_ms" in entry
    assert "summary" in entry
    assert "key_output" in entry
    assert "hallucination_score" in entry["key_output"]
    assert "unsupported_claim_count" in entry["key_output"]
    assert "claim_count" in entry["key_output"]


@patch("app.nodes.grading._grade_answer", side_effect=RuntimeError("LLM unavailable"))
def test_failure_returns_zero_score_and_error_message(mock_grade_answer):
    result = grade_hallucination(
        make_state(
            "RAG combines retrieval and generation.",
            [make_document("RAG combines retrieval with language generation.")],
        )
    )

    assert result["hallucination_score"] == 0.0
    assert "error_message" in result
    assert result["execution_trace"][0]["status"] == "error"
    mock_grade_answer.assert_called_once()


@patch("app.nodes.grading._grade_answer")
def test_empty_docs_does_not_raise(mock_grade_answer):
    result = grade_hallucination(
        make_state("RAG combines retrieval and generation.", [])
    )

    assert result["hallucination_score"] == 0.0
    assert "error_message" not in result
    assert result["execution_trace"][0]["status"] == "success"
    assert result["execution_trace"][0]["key_output"]["claim_count"] == 1
    mock_grade_answer.assert_not_called()


@patch("app.nodes.grading._grade_answer")
def test_empty_answer_does_not_raise(mock_grade_answer):
    result = grade_hallucination(
        make_state("", [make_document("RAG combines retrieval with generation.")])
    )

    assert result["hallucination_score"] == 0.0
    assert "error_message" not in result
    assert result["execution_trace"][0]["status"] == "success"
    assert result["execution_trace"][0]["key_output"]["claim_count"] == 0
    mock_grade_answer.assert_not_called()


@patch("app.nodes.grading._grade_answer")
def test_unjustified_abstention_is_capped(mock_grade_answer):
    mock_grade_answer.return_value = grading.GradingResult(
        score=1.0,
        verdict="grounded",
        explanation="The abstention sentence is supported by the documents.",
        claim_count=1,
    )

    result = grade_hallucination(
        make_state(
            "I cannot find sufficient information in the provided documents.",
            [
                make_document(
                    "Vision Transformer (ViT) applies the transformer architecture to image patches."
                )
            ],
            query="What is vision transformer?",
        )
    )

    assert result["hallucination_score"] == 0.2


@patch("app.nodes.grading._grade_answer")
def test_justified_abstention_is_capped_less_aggressively(mock_grade_answer):
    mock_grade_answer.return_value = grading.GradingResult(
        score=1.0,
        verdict="grounded",
        explanation="The abstention sentence is supported by the documents.",
        claim_count=1,
    )

    result = grade_hallucination(
        make_state(
            "I cannot find sufficient information in the provided documents.",
            [make_document("Retrieval-Augmented Generation combines retrieval with generation.")],
            query="What is the GDP of Mars?",
        )
    )

    assert result["hallucination_score"] == 0.5
