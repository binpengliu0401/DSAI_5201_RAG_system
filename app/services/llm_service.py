from functools import lru_cache

from langchain_openai import ChatOpenAI
from app.utils.constants import LLM_API_KEY, LLM_MODEL_NAME, LLM_TEMPERATURE
from config.logging import get_logger


logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_llm():
    logger.info("Initializing LLM client for model '%s'", LLM_MODEL_NAME)
    return ChatOpenAI(
        model=LLM_MODEL_NAME,
        api_key=LLM_API_KEY,  # type: ignore
        temperature=LLM_TEMPERATURE,
    )
