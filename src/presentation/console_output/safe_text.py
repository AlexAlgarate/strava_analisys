import re

_UNSAFE_TERMINAL_CHARACTERS = re.compile(
    "[\x00-\x1f\x7f-\x9f\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]"
)
_REPLACEMENT_CHARACTER = "\N{REPLACEMENT CHARACTER}"


def terminal_safe_text(value: object) -> str:
    """Render untrusted text without terminal or bidirectional control codes."""
    return _UNSAFE_TERMINAL_CHARACTERS.sub(_REPLACEMENT_CHARACTER, str(value))
