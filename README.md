# RAG Academic Paper Q&A System

A LangGraph-based Agentic RAG system for academic paper question answering,
featuring a hallucination-detection feedback loop with automatic query retry.

```
User Query
    │
    ▼
[Node 1] Query Rewriting
    │
    ▼
[Node 2] Retrieval (FAISS)
    │
    ▼
[Node 3] Generation (LLM)
    │
    ▼
[Node 4] Hallucination Grading
    │
    ▼
[Node 5] Conditional Router ── score >= 0.7 ──► Output
    │
    └── score < 0.7 & retries < max ──► back to Node 1
```

---

## Project Structure

```
app/
├── graph/
│   ├── state.py        # GraphState schema
│   ├── builder.py      # LangGraph assembly
│   └── router.py       # Conditional Router — Node 5
├── nodes/
│   ├── generation.py   # Node 3
│   ├── rewriting.py    # Node 1
│   ├── retrieval.py    # Node 2
│   └── grading.py      # Node 4
├── services/
│   ├── llm_service.py
│   └── formatter.py
├── utils/
│   ├── tracer.py
│   └── constants.py
├── api/
│   └── server.py       # FastAPI server
└── main.py             # CLI entry point

tests/
├── test_rewriting.py
├── test_retrieval.py
└── test_grading.py
```

---

## Setup

```bash
git clone <repo-url>
cd RAG_Q&A_SYSTEM

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirement.txt

cp .env.example .env
# Fill in your own API keys in .env
```

---

## Environment Variables

See `.env.example`. Each person fills in their own `.env` — never commit this file.

---

## GraphState Contract

All nodes share a single `GraphState`. Do not add or rename fields without
discussing with the system architect first.

| Field | Type | Description |
|-------|------|-------------|
| `query` | `str` | Original user question |
| `rewritten_query` | `str` | Rewritten query for retrieval |
| `failed_queries` | `Annotated[list, operator.add]` | All previously attempted queries |
| `retrieved_docs` | `List[Document]` | Retrieved LangChain Document objects |
| `answer` | `str` | Generated answer |
| `hallucination_score` | `float` | 0.0–1.0, higher = more grounded |
| `retry_count` | `int` | Current retry count |
| `max_retries` | `int` | Max retries allowed (default: 2) |
| `final_decision` | `str` | `"output"` / `"retry"` / `"stop"` |
| `error_message` | `Optional[str]` | Write here on error, do not raise |
| `execution_trace` | `Annotated[list, operator.add]` | Append-only execution log |

**Important:**

- `retrieved_docs` must be `List[Document]` from `langchain_core.documents`
- On error, write to `error_message` and return gracefully — do not raise exceptions
- Use `build_trace_entry()` from `app/utils/tracer.py` for trace entries
- Score threshold: `>= 0.7` acceptable, `< 0.7` triggers retry

---

## Unit Tests

```bash
python -m pytest tests/ -v
```
