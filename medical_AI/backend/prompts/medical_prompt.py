from __future__ import annotations

import json
from textwrap import dedent


def build_medical_prompt(report_text: str, output_schema: dict) -> str:
    """
    Build the extraction prompt.

    Parameters
    ----------
    report_text: OCR extracted text.
    
    output_schema: JSON schema (or schema template) expected from the LLM.

    Returns
    -------
    Prompt string.
    """

    output_schema = json.dumps(output_schema, indent=2)

    return dedent(f"""
    You are an expert medical laboratory report extraction assistant.

    Your task is to extract structured information from OCR text of
    pathology, laboratory and diagnostic reports.

    -----------------------------
    GENERAL RULES
    -----------------------------

    • Return ONLY valid JSON.
    • Do NOT include markdown.
    • Do NOT explain anything.
    • Do NOT wrap the response inside ```json```.
    • Do NOT hallucinate.
    • If information is unavailable, return null.

    -----------------------------
    OCR NOTES
    -----------------------------

    The OCR text may contain:

    • merged words
    • spelling mistakes
    • broken tables
    • duplicated headers
    • duplicated footers
    • page numbers
    • missing spaces
    • OCR artifacts

    Infer the intended meaning using surrounding context.

    -----------------------------
    PATIENT INFORMATION
    -----------------------------

    Extract whenever available:

    • Patient Name
    • Date of Birth
    • Age
    • Gender
    • Phone Number

    Preserve the original values.

    -----------------------------
    REPORT INFORMATION
    -----------------------------

    Extract:

    • Report Type
    • Report Date
    • Laboratory Name

    -----------------------------
    TEST RESULTS
    -----------------------------

    Extract EVERY laboratory test.

    Never skip a row.

    Never merge two different tests.

    Preserve duplicate test names if they appear.

    For every test extract:

    • test_name
    • value
    • unit
    • normal_range

    -----------------------------
    IMPORTANT
    -----------------------------

    • Keep numerical values exactly as written.
    • Keep units exactly as written.
    • Keep reference ranges exactly as written.
    • Do not calculate High/Low/Normal.
    • Do not infer missing values.
    • Preserve the report order.

    -----------------------------
    DATES
    -----------------------------

    If the date format is clear,
    convert it to

    YYYY-MM-DD

    Otherwise preserve the original value.

    -----------------------------
    OUTPUT JSON
    -----------------------------

    Return JSON matching EXACTLY this schema:

    {output_schema}

    -----------------------------
    OCR TEXT
    -----------------------------

    {report_text}
    """).strip()