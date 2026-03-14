# ============================================================
# Test for: Node 2 — Retrieval
# Run:      python -m pytest tests/test_retrieval.py -v
# Owner:    Member B (Li) — run this after your implementation
# ============================================================

import pytest
from langchain_core.documents import Document
from app.nodes.retrieval import retrieve_docs


def make_state(rewritten_query: str) -> dict:
    """Build a minimal state dict for testing."""
    pass


def test_returns_required_keys():
    """Output dict must contain: retrieved_docs, execution_trace."""
    pass


def test_retrieved_docs_is_nonempty_list():
    """retrieved_docs must be a list with at least one item."""
    pass


def test_retrieved_docs_are_document_objects():
    """CRITICAL: every item must be langchain_core.documents.Document.
    Raw strings will break the Generation node."""
    pass


def test_documents_have_nonempty_page_content():
    """Each Document must have a non-empty page_content field."""
    pass


def test_documents_have_source_in_metadata():
    """Each Document metadata must contain a 'source' field."""
    pass


def test_trace_entry_format():
    """execution_trace must have exactly 1 entry with keys:
    node, status, latency_ms, summary, key_output."""
    pass