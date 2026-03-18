import json
from functools import lru_cache

from openai import OpenAI

from app.utils.constants import LLM_API_KEY, LLM_MODEL_NAME, LLM_TEMPERATURE
from config.logging import get_logger


SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."

logger = get_logger(__name__)


class LLMService:
    """Thin wrapper around SiliconFlow's OpenAI-compatible chat API."""

    def __init__(self):
        if not LLM_API_KEY:
            raise ValueError("LLM_API_KEY is not configured.")

        self.client = OpenAI(
            api_key=LLM_API_KEY,
            base_url=SILICONFLOW_BASE_URL,
        )
        logger.info(
            "Initialized LLMService with model='%s' base_url='%s'",
            LLM_MODEL_NAME,
            SILICONFLOW_BASE_URL,
        )

    @staticmethod
    def _build_messages(prompt, system_prompt):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

    @staticmethod
    def _extract_text(response):
        try:
            message = response.choices[0].message
            content = message.content
        except (AttributeError, IndexError, KeyError, TypeError) as exc:
            raise RuntimeError("Malformed chat completion response: missing assistant message.") from exc

        if isinstance(content, str):
            text = content.strip()
        elif isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    candidate = item.get("text")
                    if isinstance(candidate, str) and candidate:
                        text_parts.append(candidate)
                else:
                    candidate = getattr(item, "text", None)
                    if isinstance(candidate, str) and candidate:
                        text_parts.append(candidate)
            text = "".join(text_parts).strip()
        else:
            text = ""

        if not text:
            raise RuntimeError("Malformed chat completion response: assistant content is empty.")
        return text

    def chat_text(
        self,
        prompt,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
    ):
        logger.info(
            "chat_text request model='%s' prompt_length=%s system_prompt_length=%s",
            LLM_MODEL_NAME,
            len(prompt),
            len(system_prompt),
        )
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL_NAME,
                temperature=LLM_TEMPERATURE,
                messages=self._build_messages(prompt, system_prompt),
            )
            return self._extract_text(response)
        except Exception as exc:
            logger.exception(
                "chat_text failed model='%s' prompt_length=%s",
                LLM_MODEL_NAME,
                len(prompt),
            )
            raise RuntimeError(f"LLM chat_text request failed: {exc}") from exc

    def chat_json(self, prompt, system_prompt):
        logger.info(
            "chat_json request model='%s' prompt_length=%s system_prompt_length=%s",
            LLM_MODEL_NAME,
            len(prompt),
            len(system_prompt),
        )
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL_NAME,
                temperature=LLM_TEMPERATURE,
                messages=self._build_messages(prompt, system_prompt),
                response_format={"type": "json_object"},
            )
            text = self._extract_text(response)
        except Exception as exc:
            logger.exception(
                "chat_json request failed model='%s' prompt_length=%s",
                LLM_MODEL_NAME,
                len(prompt),
            )
            raise RuntimeError(f"LLM chat_json request failed: {exc}") from exc

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            logger.exception("chat_json returned invalid JSON: %s", text)
            raise ValueError(f"LLM returned invalid JSON: {exc}") from exc

        if not isinstance(parsed, dict):
            raise ValueError("LLM returned JSON that is not an object.")
        return parsed

    def stream_chat(
        self,
        prompt,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
    ):
        logger.info(
            "stream_chat request model='%s' prompt_length=%s system_prompt_length=%s",
            LLM_MODEL_NAME,
            len(prompt),
            len(system_prompt),
        )
        try:
            stream = self.client.chat.completions.create(
                model=LLM_MODEL_NAME,
                temperature=LLM_TEMPERATURE,
                messages=self._build_messages(prompt, system_prompt),
                stream=True,
            )
            for chunk in stream:
                if not getattr(chunk, "choices", None):
                    continue
                delta = chunk.choices[0].delta
                token = getattr(delta, "content", None)
                if token:
                    yield token
        except Exception as exc:
            logger.exception(
                "stream_chat failed model='%s' prompt_length=%s",
                LLM_MODEL_NAME,
                len(prompt),
            )
            raise RuntimeError(f"LLM stream_chat request failed: {exc}") from exc


@lru_cache(maxsize=1)
def get_llm() -> LLMService:
    """Compatibility accessor used by the rest of the codebase."""
    return LLMService()
