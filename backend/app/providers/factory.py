import logging
from functools import lru_cache

from ..config import settings

logger = logging.getLogger("parakh.providers")


@lru_cache
def get_llm_provider():
    if settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        try:
            from .llm.anthropic_provider import AnthropicLLMProvider

            logger.info("Using Anthropic LLM provider (model=%s)", settings.ANTHROPIC_MODEL)
            return AnthropicLLMProvider()
        except Exception as exc:
            logger.warning("Falling back to mock LLM provider: %s", exc)

    if settings.LLM_PROVIDER == "groq" and settings.GROQ_API_KEY:
        try:
            from .llm.groq_provider import GroqLLMProvider

            logger.info("Using Groq LLM provider (model=%s)", settings.GROQ_MODEL)
            return GroqLLMProvider()
        except Exception as exc:
            logger.warning("Falling back to mock LLM provider: %s", exc)

    from .llm.mock_provider import MockLLMProvider

    logger.info("Using mock (offline) LLM provider")
    return MockLLMProvider()


@lru_cache
def get_search_provider():
    if settings.SEARCH_PROVIDER == "tavily" and settings.TAVILY_API_KEY:
        try:
            from .search.tavily_provider import TavilySearchProvider

            logger.info("Using Tavily search provider")
            return TavilySearchProvider()
        except Exception as exc:
            logger.warning("Falling back to mock search provider: %s", exc)

    from .search.mock_provider import MockSearchProvider

    logger.info("Using mock (offline) search provider")
    return MockSearchProvider()


@lru_cache
def get_embedding_provider():
    if settings.EMBEDDING_PROVIDER == "sentence_transformer":
        try:
            from .embeddings.sentence_transformer_provider import (
                SentenceTransformerEmbeddingProvider,
            )

            logger.info("Using sentence-transformers embedding provider")
            return SentenceTransformerEmbeddingProvider()
        except Exception as exc:
            logger.warning(
                "sentence-transformers unavailable (%s); using lightweight hashing embedding fallback.",
                exc,
            )

    from .embeddings.hashing_provider import HashingEmbeddingProvider

    logger.info("Using hashing embedding fallback provider")
    return HashingEmbeddingProvider()
