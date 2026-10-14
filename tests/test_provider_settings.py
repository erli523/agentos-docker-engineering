import os
import unittest
from unittest.mock import patch

from agno.models.openai import OpenAIResponses
from agno.models.openai.like import OpenAILike

from app.settings import default_embedder, default_model, env_enabled
from workflows.deployment_check import _check_ai_credentials


class ProviderSettingsTests(unittest.TestCase):
    def test_upstream_openai_default_is_preserved(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            model = default_model()

        self.assertIsInstance(model, OpenAIResponses)
        self.assertEqual(model.id, "gpt-5.6")

    def test_openai_compatible_model_uses_explicit_endpoint(self) -> None:
        env = {
            "AGENTOS_MODEL_ID": "compatible-chat",
            "AGENTOS_MODEL_API_KEY": "model-secret",
            "AGENTOS_MODEL_BASE_URL": "https://models.example/v1",
            "AGENTOS_MODEL_PROVIDER": "Example",
        }
        with patch.dict(os.environ, env, clear=True):
            model = default_model()

        self.assertIsInstance(model, OpenAILike)
        self.assertEqual(model.id, "compatible-chat")
        self.assertEqual(model.api_key, "model-secret")
        self.assertEqual(str(model.base_url), "https://models.example/v1")
        self.assertFalse(model.supports_native_structured_outputs)

    def test_compatible_embedder_uses_configured_dimension(self) -> None:
        env = {
            "AGENTOS_EMBEDDING_MODEL_ID": "compatible-embedding",
            "AGENTOS_EMBEDDING_API_KEY": "embedding-secret",
            "AGENTOS_EMBEDDING_BASE_URL": "https://embeddings.example/v1",
            "AGENTOS_EMBEDDING_DIMENSIONS": "1024",
        }
        with patch.dict(os.environ, env, clear=True):
            embedder = default_embedder()

        self.assertEqual(embedder.id, "compatible-embedding")
        self.assertEqual(embedder.api_key, "embedding-secret")
        self.assertEqual(embedder.base_url, "https://embeddings.example/v1")
        self.assertEqual(embedder.dimensions, 1024)

    def test_invalid_embedding_dimension_fails_early(self) -> None:
        with patch.dict(os.environ, {"AGENTOS_EMBEDDING_DIMENSIONS": "0"}, clear=True):
            with self.assertRaisesRegex(ValueError, "positive integer"):
                default_embedder()

    def test_deployment_check_accepts_split_provider_credentials(self) -> None:
        env = {
            "AGENTOS_MODEL_API_KEY": "model-secret",
            "AGENTOS_EMBEDDING_API_KEY": "embedding-secret",
        }
        with patch.dict(os.environ, env, clear=True):
            result = _check_ai_credentials()

        self.assertEqual(result.status, "PASS")
        self.assertIn("media tools remain disabled", result.detail)

    def test_deployment_check_names_missing_credential(self) -> None:
        with patch.dict(os.environ, {"AGENTOS_MODEL_API_KEY": "model-secret"}, clear=True):
            result = _check_ai_credentials()

        self.assertEqual(result.status, "FAIL")
        self.assertIn("embedding", result.detail)

    def test_optional_remote_mcp_tools_can_be_disabled(self) -> None:
        env = {"ENABLE_AGNO_DOCS_MCP": "false", "ENABLE_WEB_SEARCH": "0"}
        with patch.dict(os.environ, env, clear=True):
            self.assertFalse(env_enabled("ENABLE_AGNO_DOCS_MCP"))
            self.assertFalse(env_enabled("ENABLE_WEB_SEARCH"))


if __name__ == "__main__":
    unittest.main()
