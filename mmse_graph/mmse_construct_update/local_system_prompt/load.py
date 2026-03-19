"""Utilities for loading MMSE section system prompts from .txt files in this directory."""

from pathlib import Path

_PROMPT_DIR = Path(__file__).parent

LANGFUSE_CLIENT = None

# Ordered list of all MMSE section names (matches .txt filenames without extension).
MMSE_SECTIONS = [
    "orientation_time",
    "orientation_place",
    "registration",
    "attention_calculation",
    "recall",
    "naming",
    "repetition",
    "three_stage_command",
    "reading",
    "writing",
    "drawing",
]


def set_prompt_to_langfuse(langfuse_client):
    global LANGFUSE_CLIENT
    LANGFUSE_CLIENT = langfuse_client


def load(name: str) -> str:
    """Load and return the system prompt for the given MMSE section name.

    Args:
        name: The section name (e.g. ``"orientation_time"``). Must match one
              of the filenames (without ``.txt``) in this directory.

    Returns:
        The prompt text as a string.

    Raises:
        FileNotFoundError: If no prompt file exists for *name*.
    """
    global LANGFUSE_CLIENT
    if not LANGFUSE_CLIENT:
        prompt_path = _PROMPT_DIR / f"{name}.txt"
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"No system prompt found for section '{name}'. "
                f"Expected file: {prompt_path}"
            )
        return prompt_path.read_text(encoding="utf-8")
    # Langfuse client present
    agent_prompts = LANGFUSE_CLIENT.get_prompt(name).prompt
    return agent_prompts[0]["content"]


def load_all() -> list[tuple[str, str]]:
    """Load all MMSE section prompts in canonical test order.

    Returns:
        A list of ``(name, prompt)`` tuples, one per MMSE section.
    """
    return [(name, load(name)) for name in MMSE_SECTIONS]
