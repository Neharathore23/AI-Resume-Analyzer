"""Module 2 - text cleaning. Keeps C++, C#, .NET, CI/CD etc. and redacts personal data."""
import re

# PII Patterns for Responsible AI Compliance
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+", re.IGNORECASE)
PHONE = re.compile(
    r"(?<!\w)(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{3,5}(?!\w)"
)
URL = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
LINKEDIN = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+", re.IGNORECASE)
GITHUB = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w-]+", re.IGNORECASE)


def redact_personal_info(text: str) -> str:
    """
    Responsible-AI step: remove contact details and personal links before any analysis.
    Protects privacy and ensures candidates are evaluated purely on job-relevant skills.
    """
    if not text:
        return ""
    for pat in (EMAIL, LINKEDIN, GITHUB, URL, PHONE):
        text = pat.sub(" ", text)
    return text


def clean_text(text: str) -> str:
    """
    Lowercase, drop unneeded symbols while preserving critical domain tokens
    (keeps C++, C#, .NET, CI/CD, etc.), and collapse whitespace.
    """
    text = redact_personal_info(text or "").lower()
    # Keep alphanumeric, +, #, ., /, -, and whitespace
    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)
    # Strip stray punctuation (periods, slashes, hyphens) but preserve .net, c++, c#, ci/cd
    text = re.sub(r"(?<![a-z0-9])(?!\.net\b)[./\-]+|[./\-]+(?![a-z0-9+#])", " ", text)
    # Collapse multiple whitespaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()

