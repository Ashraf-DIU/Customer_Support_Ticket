"""Text cleaning. KEEP IDENTICAL to ml/train.py -> clean_text / build_text."""
import re

_PLACEHOLDER = re.compile(r"\{[^}]*\}")
_WS = re.compile(r"\s+")


def clean_text(text: str) -> str:
    text = _PLACEHOLDER.sub(" ", str(text))
    return _WS.sub(" ", text).strip().lower()


def build_text(subject: str, message: str) -> str:
    return clean_text(f"{subject}. {message}")
