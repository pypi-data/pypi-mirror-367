from dataclasses import dataclass
from datetime import datetime
from typing import Any, Union, Optional, Dict, List

MODEL_MAPPINGS = {
    "openai": [
        # GPT-4.1 variants
        "gpt-4.1",
        "gpt-4.1-mini",
        # GPT-4o variants
        "gpt-4o-mini",
        "gpt-4o",
        # o1
        "o1",  # -> o1-2024-12-17
        # o3
        "o3",
        "o3-low",
        "o3-medium",
        "o3-high",
        # o3 mini
        "o3-mini",
        "o3-mini-low",
        "o3-mini-medium",
        "o3-mini-high",
        # o4 mini
        "o4-mini",
        "o4-mini-low",
        "o4-mini-medium",
        "o4-mini-high",
    ],
    "claude": [
        # Claude 3.5 variants
        "claude-3-5-sonnet-latest",
        "claude-3-5-haiku-latest",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        # Claude 3 variants
        "claude-3-sonnet-20240229",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307",
        # Claude 2 variants
        "claude-2.1",
        "claude-2.0",
        # Claude instant
        "claude-instant-1.2",
        # Sonnet 4
        "claude-sonnet-4-20250514",
    ],
    "gemini": [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ],
    "grok": [
        "grok-3-mini",
        "grok-3",
        "grok-4",
    ],
}


def get_backend_type_from_model(model: str) -> str:
    """
    Determine the agent type based on the model name.

    Args:
        model: The model name (e.g., "gpt-4", "gemini-pro", "grok-1")

    Returns:
        Agent type string ("openai", "gemini", "grok")
    """
    if not model:
        return "openai"  # Default to OpenAI

    model_lower = model.lower()

    for key, models in MODEL_MAPPINGS.items():
        if model_lower in models:
            return key
    raise ValueError(f"Unknown model: {model}")
