"""
App Settings
============

Shared runtime objects for the platform.
"""

from os import getenv

from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.models.openai import OpenAIResponses
from agno.models.openai.like import OpenAILike


def env_enabled(name: str, *, default: bool = True) -> bool:
    """Read a conventional boolean environment flag."""
    value = getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def default_model() -> OpenAIResponses | OpenAILike:
    """Return a fresh model, optionally backed by an OpenAI-compatible API.

    The upstream OpenAI Responses default remains intact when no compatible
    endpoint is configured. Providers such as DeepSeek expose Chat Completions,
    so they use ``OpenAILike`` instead of the Responses adapter.
    """
    model_id = getenv("AGENTOS_MODEL_ID", "gpt-5.6")
    api_key = getenv("AGENTOS_MODEL_API_KEY") or getenv("OPENAI_API_KEY")
    base_url = getenv("AGENTOS_MODEL_BASE_URL")

    if base_url:
        return OpenAILike(
            id=model_id,
            name=getenv("AGENTOS_MODEL_PROVIDER", "OpenAI-compatible"),
            provider=getenv("AGENTOS_MODEL_PROVIDER", "OpenAI-compatible"),
            api_key=api_key or "not-provided",
            base_url=base_url,
            supports_native_structured_outputs=False,
            strict_output=False,
        )
    return OpenAIResponses(id=model_id, api_key=api_key)


def default_embedder() -> OpenAIEmbedder:
    """Return the configured OpenAI-compatible knowledge embedder."""
    raw_dimensions = getenv("AGENTOS_EMBEDDING_DIMENSIONS")
    dimensions = int(raw_dimensions) if raw_dimensions else None
    if dimensions is not None and dimensions <= 0:
        raise ValueError("AGENTOS_EMBEDDING_DIMENSIONS must be a positive integer")

    return OpenAIEmbedder(
        id=getenv("AGENTOS_EMBEDDING_MODEL_ID", "text-embedding-3-small"),
        api_key=getenv("AGENTOS_EMBEDDING_API_KEY") or getenv("OPENAI_API_KEY"),
        base_url=getenv("AGENTOS_EMBEDDING_BASE_URL"),
        dimensions=dimensions,
    )
