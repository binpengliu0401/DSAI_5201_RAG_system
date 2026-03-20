from app.services.llm_service import LLMService


def test_live_chat_text_returns_non_empty_string():
    service = LLMService()

    result = service.chat_text(
        "What is Retrieval-Augmented Generation? Answer in one short paragraph."
    )

    assert isinstance(result, str)
    assert result.strip()


def test_live_chat_json_returns_dict():
    service = LLMService()

    result = service.chat_json(
        prompt=(
            'Return a JSON object with keys "term" and "benefit". '
            "Describe RAG briefly."
        ),
        system_prompt="You are a precise assistant that returns valid JSON only.",
    )

    assert isinstance(result, dict)
    assert "term" in result
    assert "benefit" in result


def test_live_stream_chat_returns_tokens():
    service = LLMService()

    tokens = list(
        service.stream_chat("Explain RAG in one or two short sentences.")
    )

    assert tokens
    assert any(token.strip() for token in tokens)
