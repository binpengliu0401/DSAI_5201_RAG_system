# Owner: Liu
# Responsibility: Execution trace helper — used by all nodes


def build_trace_entry(
    node: str,
    status: str,
    latency_ms: float,
    summary: str,
    key_output: dict = {}
) -> dict:
    """
    Build a single execution trace entry.

    Args:
        node:        node name, e.g. "generation"
        status:      "success" or "error"
        latency_ms:  time taken in milliseconds
        summary:     one-line human-readable description
        key_output:  key results to surface for frontend / demo display

    Returns:
        A dict to be appended to execution_trace in GraphState.
    """
    return {
        "node": node,
        "status": status,
        "latency_ms": latency_ms,
        "summary": summary,
        "key_output": key_output
    }