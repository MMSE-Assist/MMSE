"""Utilities for loading MMSE section system prompts from .txt files in this directory."""

from pathlib import Path

_PROMPT_DIR = Path(__file__).parent

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
    prompt_path = _PROMPT_DIR / f"{name}.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(
            f"No system prompt found for section '{name}'. "
            f"Expected file: {prompt_path}"
        )
    return prompt_path.read_text(encoding="utf-8")


def load_all() -> list[tuple[str, str]]:
    """Load all MMSE section prompts in canonical test order.

    Returns:
        A list of ``(name, prompt)`` tuples, one per MMSE section.
    """
    return [(name, load(name)) for name in MMSE_SECTIONS]
