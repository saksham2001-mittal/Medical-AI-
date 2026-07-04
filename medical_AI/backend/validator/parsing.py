from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any
from dateutil import parser as date_parser


# ---------------------------------------------------------------------
# Generic String
# ---------------------------------------------------------------------

def clean_string(value: Any) -> str | None:
    """
    Convert any value into a cleaned string.

    Returns None if value is empty.
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return text


# ---------------------------------------------------------------------
# Integer
# ---------------------------------------------------------------------

def parse_int(value: Any) -> int | None:

    if value is None:
        return None

    if isinstance(value, int):
        return value

    text = clean_string(value)

    if text is None:
        return None

    match = re.search(r"-?\d+", text)

    return int(match.group()) if match else None


# ---------------------------------------------------------------------
# Float
# ---------------------------------------------------------------------

def parse_float(value: Any) -> float | None:

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = clean_string(value)

    if text is None:
        return None

    match = re.search(r"-?\d+(?:\.\d+)?", text)

    return float(match.group()) if match else None


# ---------------------------------------------------------------------
# Age
# ---------------------------------------------------------------------

def parse_age(value: Any) -> int | None:
    
    age = parse_int(value)

    if age is None:
        return None

    if 0 <= age <= 130:
        return age

    return None


# ---------------------------------------------------------------------
# Gender
# ---------------------------------------------------------------------

_GENDER_MAP = {
    "m": "Male",
    "male": "Male",
    "f": "Female",
    "female": "Female",
    "o": "Other",
    "other": "Other",
}


def parse_gender(value: Any) -> str | None:

    text = clean_string(value)

    if text is None:
        return None

    return _GENDER_MAP.get(text.lower())


# ---------------------------------------------------------------------
# Date
# ---------------------------------------------------------------------

def parse_date(value: Any) -> date | None:
    """
    Supports almost every common medical date format.

    """

    if value is None:
        return None

    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    if isinstance(value, datetime):
        return value.date()

    text = clean_string(value)

    if text is None:
        return None

    try:
        return date_parser.parse(
            text,
            fuzzy=True
        ).date()

    except Exception:
        return None


# ---------------------------------------------------------------------
# Normalize entire extracted report
# ---------------------------------------------------------------------

def normalize_extracted_json(data: dict) -> dict:
    """
    Normalize raw LLM JSON before Pydantic validation.
    """

    if not isinstance(data, dict):
        return data

    patient = data.get("patient_info", {})

    if isinstance(patient, dict):

        patient["patient_name"] = clean_string(
            patient.get("patient_name")
        ) or ""

        patient["phone_no"] = clean_string(
            patient.get("phone_no")
        )

        patient["age"] = parse_age(
            patient.get("age")
        )

        patient["gender"] = parse_gender(
            patient.get("gender")
        )

        patient["date_of_birth"] = parse_date(
            patient.get("date_of_birth")
        )

    report = data.get("report_info", {})

    if isinstance(report, dict):

        report["report_type"] = clean_string(
            report.get("report_type")
        ) or ""

        report["lab_name"] = clean_string(
            report.get("lab_name")
        ) or ""

        report["report_date"] = parse_date(
            report.get("report_date")
        )

    tests = data.get("test_results", [])

    if isinstance(tests, list):

        for test in tests:

            if not isinstance(test, dict):
                continue

            test["test_name"] = clean_string(
                test.get("test_name")
            ) or ""

            test["value"] = clean_string(
                test.get("value")
            ) or ""

            test["unit"] = clean_string(
                test.get("unit")
            ) or ""

            test["normal_range"] = clean_string(
                test.get("normal_range")
            ) or ""

            test["status"] = clean_string(
                test.get("status")
            ) or ""

    return data