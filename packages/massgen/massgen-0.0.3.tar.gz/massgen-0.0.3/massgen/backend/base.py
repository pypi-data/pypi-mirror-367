from __future__ import annotations

"""
Base backend interface for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, AsyncGenerator, Optional
from dataclasses import dataclass


@dataclass
class StreamChunk:
    """Standardized chunk format for streaming responses."""

    type: str  # "content", "tool_calls", "builtin_tool_results", "complete_message", "complete_response", "done", "error", "agent_status"
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = (
        None  # User-defined function tools (need execution)
    )
    builtin_tool_results: Optional[List[Dict[str, Any]]] = (
        None  # Provider builtin tools (already executed)
    )
    complete_message: Optional[Dict[str, Any]] = None  # Complete assistant message
    response: Optional[Dict[str, Any]] = None  # Raw Responses API response
    error: Optional[str] = None
    source: Optional[str] = None  # Source identifier (e.g., agent_id, "orchestrator")
    status: Optional[str] = None  # For agent status updates


@dataclass
class TokenUsage:
    """Token usage and cost tracking."""

    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0


class LLMBackend(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        self.token_usage = TokenUsage()

    @abstractmethod
    async def stream_with_tools(
        self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Stream a response with tool calling support.

        Args:
            messages: Conversation messages
            tools: Available tools schema
            **kwargs: Additional provider-specific parameters including model

        Yields:
            StreamChunk: Standardized response chunks
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        pass

    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        pass

    @abstractmethod
    def calculate_cost(
        self, input_tokens: int, output_tokens: int, model: str
    ) -> float:
        """Calculate cost for token usage."""
        pass

    def update_token_usage(
        self, messages: List[Dict[str, Any]], response_content: str, model: str
    ):
        """Update token usage tracking."""
        # Estimate input tokens from messages
        input_text = str(messages)
        input_tokens = self.estimate_tokens(input_text)

        # Estimate output tokens from response
        output_tokens = self.estimate_tokens(response_content)

        # Update totals
        self.token_usage.input_tokens += input_tokens
        self.token_usage.output_tokens += output_tokens

        # Calculate cost
        cost = self.calculate_cost(input_tokens, output_tokens, model)
        self.token_usage.estimated_cost += cost

    def get_token_usage(self) -> TokenUsage:
        """Get current token usage."""
        return self.token_usage

    def reset_token_usage(self):
        """Reset token usage tracking."""
        self.token_usage = TokenUsage()

    def get_supported_builtin_tools(self) -> List[str]:
        """Get list of builtin tools supported by this provider."""
        return []

    def extract_tool_name(self, tool_call: Dict[str, Any]) -> str:
        """
        Extract tool name from a tool call in this backend's format.

        Args:
            tool_call: Tool call data structure from this backend

        Returns:
            Tool name string
        """
        # Default implementation assumes Chat Completions format
        return tool_call.get("function", {}).get("name", "unknown")

    def extract_tool_arguments(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract tool arguments from a tool call in this backend's format.

        Args:
            tool_call: Tool call data structure from this backend

        Returns:
            Tool arguments dictionary
        """
        # Default implementation assumes Chat Completions format
        return tool_call.get("function", {}).get("arguments", {})

    def extract_tool_call_id(self, tool_call: Dict[str, Any]) -> str:
        """
        Extract tool call ID from a tool call in this backend's format.

        Args:
            tool_call: Tool call data structure from this backend

        Returns:
            Tool call ID string
        """
        # Default implementation assumes Chat Completions format
        return tool_call.get("id", "")

    def create_tool_result_message(
        self, tool_call: Dict[str, Any], result_content: str
    ) -> Dict[str, Any]:
        """
        Create a tool result message in this backend's expected format.

        Args:
            tool_call: Original tool call data structure
            result_content: The result content to send back

        Returns:
            Tool result message in backend's expected format
        """
        # Default implementation assumes Chat Completions format
        tool_call_id = self.extract_tool_call_id(tool_call)
        return {"role": "tool", "tool_call_id": tool_call_id, "content": result_content}

    def extract_tool_result_content(self, tool_result_message: Dict[str, Any]) -> str:
        """
        Extract the content/output from a tool result message in this backend's format.

        Args:
            tool_result_message: Tool result message created by this backend

        Returns:
            The content/output string from the message
        """
        # Default implementation assumes Chat Completions format
        return tool_result_message.get("content", "")
