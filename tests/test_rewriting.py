# ============================================================
# Test for: Node 1 — Query Rewriting
# Run:      python -m pytest tests/test_rewriting.py -v
# Owner:    Member C (Chen) — run this after your implementation
# ============================================================

import pytest
from app.nodes.rewriting import rewrite_query


def make_state(query: str, failed_queries: list = []) -> dict:
    """Build a minimal state dict for testing."""
    pass


def test_returns_required_keys():
    """Output dict must contain: rewritten_query, failed_queries, execution_trace."""
    pass


def test_rewritten_query_is_nonempty_string():
    """rewritten_query must be a non-empty string."""
    pass


def test_rewritten_query_differs_from_original():
    """Rewritten query should not be identical to the original input."""
    pass


def test_failed_queries_contains_new_query():
    """failed_queries must include the newly rewritten query."""
    pass


def test_retry_avoids_previous_queries():
    """On retry, rewritten_query must not repeat any query in failed_queries.
    If it does, the router will enter a dead loop."""
    pass


def test_trace_entry_format():
    """execution_trace must have exactly 1 entry with keys:
    node, status, latency_ms, summary, key_output."""
    pass