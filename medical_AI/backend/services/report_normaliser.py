from __future__ import annotations

import re
import unicodedata


def normalize_raw_ocr_text(text: str) -> str:
    """
    Perform safe normalization before sending OCR text to the LLM.
    """

    if not text:
        return ""

    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)
    # Standardize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove control characters except newline/tab
    text = re.sub(r"[\x00-\x08\x0B-\x1F\x7F]", "", text)
    # Remove zero-width characters
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)
    # Normalize tabs
    text = text.replace("\t", " ")
    # Collapse multiple spaces
    text = re.sub(r"[ ]{2,}", " ", text)
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing spaces
    text = "\n".join(line.rstrip() for line in text.splitlines())
    # normalize spacing around labels
    text = _fix_label_spacing(text)
    return text.strip()


def _fix_label_spacing(text: str) -> str:
    """
    Normalize spacing around labels.
    """

    # Ensure one space after colon
    text = re.sub(r":\s*", ": ", text)

    # Remove multiple spaces after colon
    text = re.sub(r":\s{2,}", ": ", text)
    return text
