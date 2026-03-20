from unittest.mock import MagicMock, patch

import pytest

from app.services import llm_service


def make_response(text):
    message = MagicMock()
    message.content = text

    choice = MagicMock()
    choice.message = message

    response = MagicMock()
    response.choices = [choice]
    return response


def make_stream_chunk(text):
    delta = MagicMock()
    delta.content = text

    choice = MagicMock()
    choice.delta = delta

    chunk = MagicMock()
    chunk.choices = [choice]
    return chunk


def expected_messages(user_prompt, system_prompt):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


@patch("app.services.llm_service.LLM_API_KEY", "test-key")
@patch("app.services.llm_service.OpenAI")
def test_constructor_initializes_openai_client(mock_openai):
    service = llm_service.LLMService()  # type: ignore

    mock_openai.assert_called_once_with(
        api_key="test-key",
        base_url=llm_service.SILICONFLOW_BASE_URL,  # type: ignore
    )
    assert service.client is mock_openai.return_value


@patch("app.services.llm_service.LLM_API_KEY", "test-key")
@patch("app.services.llm_service.OpenAI")
def test_chat_text_returns_assistant_text(mock_openai):
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.return_value = make_response(
        "RAG improves grounding."
    )

    service = llm_service.LLMService()  # type: ignore
    result = service.chat_text("What is RAG?")

    assert result == "RAG improves grounding."
    mock_client.chat.completions.create.assert_called_once_with(
        model=llm_service.LLM_MODEL_NAME,  # type: ignore
        temperature=llm_service.LLM_TEMPERATURE,
        messages=expected_messages(
            "What is RAG?",
            llm_service.DEFAULT_SYSTEM_PROMPT,  # type: ignore
        ),
    )


@patch("app.services.llm_service.LLM_API_KEY", "test-key")
@patch("app.services.llm_service.OpenAI")
def test_chat_json_returns_parsed_dict(mock_openai):
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.return_value = make_response(
        '{"label":"RAG","summary":"Grounds answers with retrieval."}'
    )

    service = llm_service.LLMService()  # type: ignore
    result = service.chat_json(
        "Return JSON describing RAG.",
        "You must return valid JSON.",
    )

    assert result == {
        "label": "RAG",
        "summary": "Grounds answers with retrieval.",
    }
    mock_client.chat.completions.create.assert_called_once_with(
        model=llm_service.LLM_MODEL_NAME,  # type: ignore
        temperature=llm_service.LLM_TEMPERATURE,
        messages=expected_messages(
            "Return JSON describing RAG.",
            "You must return valid JSON.",
        ),
        response_format={"type": "json_object"},
    )


@patch("app.services.llm_service.LLM_API_KEY", "test-key")
@patch("app.services.llm_service.OpenAI")
def test_chat_json_raises_for_invalid_json(mock_openai):
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.return_value = make_response("not json")

    service = llm_service.LLMService()  # type: ignore

    with pytest.raises(ValueError, match="LLM returned invalid JSON"):
        service.chat_json(
            "Return JSON describing RAG.",
            "You must return valid JSON.",
        )


@patch("app.services.llm_service.LLM_API_KEY", "test-key")
@patch("app.services.llm_service.OpenAI")
def test_stream_chat_yields_only_non_empty_tokens(mock_openai):
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.return_value = [
        make_stream_chunk("RAG "),
        make_stream_chunk(None),
        make_stream_chunk("improves "),
        make_stream_chunk("grounding."),
    ]

    service = llm_service.LLMService()  # type: ignore
    tokens = list(service.stream_chat("Explain RAG briefly"))

    assert tokens == ["RAG ", "improves ", "grounding."]
    mock_client.chat.completions.create.assert_called_once_with(
        model=llm_service.LLM_MODEL_NAME,  # type: ignore
        temperature=llm_service.LLM_TEMPERATURE,
        messages=expected_messages(
            "Explain RAG briefly",
            llm_service.DEFAULT_SYSTEM_PROMPT,  # type: ignore
        ),
        stream=True,
    )


@patch("app.services.llm_service.LLM_API_KEY", None)
def test_constructor_requires_api_key():
    with pytest.raises(ValueError, match="LLM_API_KEY is not configured"):
        llm_service.LLMService()  # type: ignore
