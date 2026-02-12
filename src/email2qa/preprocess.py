from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup

_QUOTE_PATTERNS = [
    re.compile(r"^On .+wrote:$", re.IGNORECASE),
    re.compile(r"^From:\s", re.IGNORECASE),
    re.compile(r"^Sent:\s", re.IGNORECASE),
    re.compile(r"^-----Original Message-----", re.IGNORECASE),
]

_SIGNATURE_PATTERNS = [
    re.compile(r"^thanks[,]?$", re.IGNORECASE),
    re.compile(r"^best regards[,]?$", re.IGNORECASE),
    re.compile(r"^kind regards[,]?$", re.IGNORECASE),
]

_DISCLAIMER_MARKERS = [
    "This email and any attachments",
    "Confidentiality Notice",
    "The information contained in this e-mail",
]


@dataclass(frozen=True)
class PreprocessResult:
    cleaned_text: str
    has_enough_content: bool


def html_to_text(raw_body: str) -> str:
    if "<" not in raw_body and ">" not in raw_body:
        return raw_body
    soup = BeautifulSoup(raw_body, "html.parser")
    return soup.get_text("\n")


def strip_quoted_text(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        trimmed = line.strip()
        if any(pattern.match(trimmed) for pattern in _QUOTE_PATTERNS):
            break
        if trimmed.startswith(">"):
            break
        lines.append(line)
    return "\n".join(lines)


def strip_disclaimer(text: str) -> str:
    for marker in _DISCLAIMER_MARKERS:
        index = text.find(marker)
        if index >= 0:
            return text[:index]
    return text


def trim_signature(text: str) -> str:
    lines = text.splitlines()
    cutoff = len(lines)
    for idx, line in enumerate(lines):
        if any(pattern.match(line.strip()) for pattern in _SIGNATURE_PATTERNS):
            cutoff = idx
            break
    return "\n".join(lines[:cutoff])


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[\t ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def preprocess_email_body(raw_body: str) -> PreprocessResult:
    text = html_to_text(raw_body)
    text = strip_disclaimer(text)
    text = strip_quoted_text(text)
    text = trim_signature(text)
    text = normalize_whitespace(text)

    enough = len(text) >= 50 and len(text.split()) >= 10
    return PreprocessResult(cleaned_text=text, has_enough_content=enough)
