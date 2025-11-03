"""
LLM Adapter for ForgeBase.

Provides abstract interface for integrating with Large Language Models.

:author: ForgeBase Development Team
:since: 2025-11-03
"""

from abc import abstractmethod
from typing import Any

from forgebase.adapters.adapter_base import AdapterBase


class LLMAdapter(AdapterBase):
    """
    Abstract adapter for LLM integration.

    Provides interface for prompt-based AI interactions.

    Example::

        class OpenAIAdapter(LLMAdapter):
            def complete(self, prompt, **kwargs):
                # OpenAI implementation
                return response

        adapter = OpenAIAdapter(api_key="...")
        result = adapter.complete("Explain quantum computing")
    """

    @abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> str:
        """
        Send prompt and get completion.

        :param prompt: Input prompt
        :type prompt: str
        :param kwargs: Provider-specific options
        :type kwargs: Any
        :return: Completion text
        :rtype: str
        """
        pass

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """
        Chat with context.

        :param messages: Chat history
        :type messages: List[Dict[str, str]]
        :param kwargs: Provider-specific options
        :type kwargs: Any
        :return: Response text
        :rtype: str
        """
        pass

    def name(self) -> str:
        """Get adapter name."""
        return "LLMAdapter"

    def module(self) -> str:
        """Get module name."""
        return "forgebase.adapters.ai"

    def _instrument(self) -> None:
        """Instrument adapter."""
        pass


class MockLLMAdapter(LLMAdapter):
    """
    Mock LLM adapter for testing.

    Returns predefined responses without calling real APIs.
    """

    def __init__(self, responses: dict[str, str] | None = None):
        """
        Initialize mock adapter.

        :param responses: Dictionary mapping prompts to responses
        :type responses: Optional[Dict[str, str]]
        """
        self.responses = responses or {}
        self.call_count = 0

    def complete(self, prompt: str, **kwargs: Any) -> str:
        """Return mock completion."""
        self.call_count += 1
        return self.responses.get(prompt, f"Mock response to: {prompt}")

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Return mock chat response."""
        self.call_count += 1
        last_message = messages[-1]['content'] if messages else ""
        return self.responses.get(last_message, "Mock chat response")
