from datetime import datetime


# def parse_age(age_str: str):
#     try:
#         digits = ''.join(filter(str.isdigit, age_str))
#         return int(digits) if digits else None
#     except:
#         return None

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
    if not date_str:
        return None

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d %b %Y",
        "%d %B %Y",
        "%d/%b/%Y",
        "%d/%B/%Y"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # if parsed value has no time component, combine with current time
            if dt.time() == datetime.min.time():
                now_time = datetime.now().time()
                return datetime.combine(dt.date(), now_time)
            return dt
        except:
            pass

    return None