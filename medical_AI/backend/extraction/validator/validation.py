from __future__ import annotations
import re
from typing import Optional

NULL_VALUES = {
    "",
    "-",
    "--",
    "na",
    "n/a",
    "null",
    "none",
    "unknown",
    "not found",
}


# ---------------------------------------------------------------------
# Generic
# ---------------------------------------------------------------------

def is_empty(value: Optional[str]) -> bool:

    if value is None:
        return True

    return str(value).strip().lower() in NULL_VALUES


# ---------------------------------------------------------------------
# Patient Name
# ---------------------------------------------------------------------

def normalize_patient_name(name: Optional[str]) -> Optional[str]:

    if is_empty(name):
        return None

    name = " ".join(name.split())
    name = re.sub(r"[^A-Za-z\s.'-]","",name,)
    return name.strip().title() or None


def validate_patient_name(name: Optional[str]) -> bool:

    if is_empty(name):
        return False

    name = normalize_patient_name(name)
    if name is None:
        return False
    if len(name.split()) < 2:
        return False
    return True

# ---------------------------------------------------------------------
# Phone
# ---------------------------------------------------------------------

def parse_phone(phone: Optional[str]) -> Optional[str]:

    if is_empty(phone):
        return None

    digits = re.sub(r"\D", "", phone)

    if len(digits) < 10:
        return None

    return digits[-10:]


# ---------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def parse_email(email: Optional[str]) -> Optional[str]:

    if is_empty(email):
        return None

    email = email.strip().lower()

    if EMAIL_PATTERN.match(email):
        return email

    return None


# ---------------------------------------------------------------------
# Reference Range
# ---------------------------------------------------------------------

def normalize_reference_range(
    value: Optional[str],
) -> Optional[str]:

    if is_empty(value):
        return None

    value = value.replace("to", "-")
    value = value.replace("–", "-")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ---------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------

_UNIT_MAP = {
    "mgdl": "mg/dL",
    "gdl": "g/dL",
    "mmoll": "mmol/L",
    "iul": "IU/L",
}


def normalize_unit(
    unit: Optional[str],
) -> Optional[str]:

    if is_empty(unit):
        return None

    key = unit.strip().lower().replace("/", "")

    return _UNIT_MAP.get(key, unit.strip())


# ---------------------------------------------------------------------
# Test Name
# ---------------------------------------------------------------------

def normalize_test_name(
    name: Optional[str],
) -> Optional[str]:

    if is_empty(name):
        return None

    return " ".join(name.split())