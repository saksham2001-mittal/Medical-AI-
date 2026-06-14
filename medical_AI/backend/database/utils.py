from datetime import datetime
import re

def parse_age(age):

    if age is None:
        return None

    if isinstance(age, int):
        return age

    match = re.search(r"\d+", str(age))

    if match:
        return int(match.group())

    return None

def parse_date(date_str: str):
    if not date_str and date_str== "Not Found":
        return None

    formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %b %Y", "%d %B %Y", "%d/%b/%Y", "%d/%B/%Y"]

    # for fmt in formats:
    #     try:
    #         dt = datetime.strptime(date_str, fmt)
    #         # if parsed value has no time component, combine with current time
    #         if dt.time() == datetime.min.time():
    #             now_time = datetime.now().time()
    #             return datetime.combine(dt.date(), now_time)
    #         return dt
    #     except:
    #         pass
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except:
            pass

    return None

import re


def validate_patient_name(name: str):

    if not name:
        return False

    # remove extra spaces
    name = " ".join(name.split())

    # only alphabets and spaces
    if not re.fullmatch(r"[A-Za-z ]+", name):
        return False

    # minimum 2 words
    if len(name.split()) < 2:
        return False

    return True

def normalize_patient_name(name: str):

    name = " ".join(name.split())
    return name.title()