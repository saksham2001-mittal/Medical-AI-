from typing import List, Dict, Any
import re
from datetime import date

class ComparisonEngine:

    def compare_test(self, reports: List[Dict[str, Any]], test_name: str) -> Dict[str, Any]:

        measurements = []

        for report in reports:

            report_date = report.get("report_date")

            if not report_date:
                continue

            for test in report.get("tests", []):

                current_test_name = test.get("test_name", "")

                # Matches requested test against the actual test name stored in the report.
                if not self._test_name_matches(test_name, current_test_name):
                    continue

                raw_value = test.get("result")

                value = self._parse_numeric(raw_value)

                # Skip values that cannot safely be treated as a single numeric measurement.
                if value is None:
                    continue

                measurements.append(
                    {
                        "date": report_date,
                        "value": value,
                        "unit": test.get("unit", ""),
                        "reference_range": test.get("normal_range", ""),
                    }
                )
                # Only one matching test per report is needed.
                break

        # ---------------------------------------------------------
        # Sort chronologically
        # ---------------------------------------------------------
        measurements.sort(key=lambda item: self._parse_date(item["date"]))

        # ---------------------------------------------------------
        # Not enough usable data
        # ---------------------------------------------------------

        if not measurements:
            return {
                "test_name": test_name,
                "measurements": [],
                "changes": [],
                "overall_trend": "Insufficient Data",
                "latest_change": "Insufficient Data",
                "latest_value": None,
                "previous_value": None,
                "latest_status": "Unknown",
                "reference_range": "",
            }

        # ---------------------------------------------------------
        # Calculate changes between consecutive reports
        # ---------------------------------------------------------

        changes = []

        for previous, current in zip(measurements, measurements[1:]):

            change = (current["value"] - previous["value"])

            if change > 0:
                direction = "increased"

            elif change < 0:
                direction = "decreased"

            else:
                direction = "stable"

            changes.append(
                {
                    "from_date": previous["date"],
                    "to_date": current["date"],
                    "from_value": previous["value"],
                    "to_value": current["value"],
                    "change": round(change, 4),
                    "direction": direction,
                }
            )
        # ---------------------------------------------------------
        # Overall mathematical trend
        # ---------------------------------------------------------

        overall_trend = self._determine_trend(measurements)

        # ---------------------------------------------------------
        # Latest vs previous report
        # ---------------------------------------------------------

        latest_value = measurements[-1]["value"]

        latest_reference_range = measurements[-1].get("reference_range", "")

        previous_value = None
        latest_change = "Insufficient Data"

        if len(measurements) >= 2:

            previous_value = measurements[-2]["value"]

            if latest_value > previous_value:
                latest_change = "Increased"

            elif latest_value < previous_value:
                latest_change = "Decreased"
            else:
                latest_change = "Stable"

        # ---------------------------------------------------------
        # Latest reference-range status
        # ---------------------------------------------------------

        latest_status = self._determine_reference_status(latest_value, latest_reference_range)

        # ---------------------------------------------------------
        # Final comparison result
        # ---------------------------------------------------------

        return {
            "test_name": test_name,

            "measurements": measurements,

            "changes": changes,

            # Overall historical behavior
            "overall_trend": overall_trend,

            # Latest report vs immediately previous report
            "latest_change": latest_change,

            "latest_value": latest_value,

            "previous_value": previous_value,

            # Latest report's reference range
            "reference_range": latest_reference_range,

            # Latest value relative to reference range
            "latest_status": latest_status,
        }

    # =========================================================
    # DATE PARSING
    # =========================================================

    @staticmethod
    def _parse_date(value):

        if isinstance(value, date):
            return value

        if not value:
            return date.max

        value = str(value).strip()

        try:
            return date.fromisoformat(value)

        except ValueError:
            # Keep the original behavior from failing completely
            # if an unexpected date format appears.
            return date.max

    # =========================================================
    # TEST-NAME MATCHING
    # =========================================================

    @staticmethod
    def _test_name_matches(requested_name: str, actual_name: str) -> bool:

        requested = ComparisonEngine._normalize(requested_name)

        actual = ComparisonEngine._normalize(actual_name)

        # -----------------------------------------------------
        # Exact match
        # -----------------------------------------------------

        if requested == actual:
            return True

        # -----------------------------------------------------
        # Token-based matching
        # -----------------------------------------------------

        requested_tokens = set(requested.split())

        actual_tokens = set(actual.split())

        if not requested_tokens:
            return False

        common_tokens = (requested_tokens & actual_tokens)

        meaningful_tokens = {token for token in requested_tokens if len(token) > 1}

        if (meaningful_tokens and len(common_tokens)/len(meaningful_tokens)>= 0.5):
            return True

        return False

    # =========================================================
    # NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize(value: str) -> str:

        value = str(value).strip().casefold()

        # Replace punctuation with spaces
        value = re.sub(r"[^a-z0-9]+"," ",value)
        # Remove extra whitespace
        value = re.sub(r"\s+", " ",value)
        return value.strip()

    # =========================================================
    # NUMERIC PARSING
    # =========================================================

    @staticmethod
    def _parse_numeric(value):

        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        value = str(value).strip()

        if not value:
            return None

        # -----------------------------------------------------
        # Values such as "Nil", "Negative", "Trace"
        # are not single numeric measurements.
        # -----------------------------------------------------

        non_numeric_values = {
            "nil",
            "negative",
            "positive",
            "trace",
            "normal",
            "absent",
            "present",
        }

        if value.casefold() in non_numeric_values:
            return None

        if re.search(r"\d+\s*-\s*\d+",value):
            return None

        # Remove commas
        value = value.replace(",", "")

        # Direct numeric value
        try:
            return float(value)

        except ValueError:
            pass

        # Extract a single numeric value
        match = re.fullmatch(r"\s*[-+]?\d*\.?\d+\s*.*",value)

        if match:
            number_match = re.search(r"[-+]?\d*\.?\d+",value)
            if number_match:
                try:
                    return float(number_match.group())
                except ValueError:
                    return None

        return None

    # =========================================================
    # TREND CALCULATION
    # =========================================================

    @staticmethod
    def _determine_trend(measurements):

        if len(measurements) < 2:
            return "Insufficient Data"

        values = [item["value"] for item in measurements]

        increases = 0
        decreases = 0

        for previous, current in zip(values, values[1:]):
            if current > previous:
                increases += 1
            elif current < previous:
                decreases += 1

        if increases and decreases:
            return "Fluctuating"

        if increases:
            return "Increasing"

        if decreases:
            return "Decreasing"

        return "Stable"

    # =========================================================
    # REFERENCE RANGE STATUS
    # =========================================================

    @staticmethod
    def _determine_reference_status(value: float, reference_range: str) -> str:

        if value is None:
            return "Unknown"

        if not reference_range:
            return "Reference Range Unavailable"

        reference_range = str(reference_range).strip()

        # -----------------------------------------------------
        # Normalize common dash characters
        # -----------------------------------------------------

        reference_range = (reference_range.replace("-", "-").replace("—", "-"))

        range_match = re.search(
            r"([-+]?\d*\.?\d+)"
            r"\s*-\s*"
            r"([-+]?\d*\.?\d+)", reference_range
        )

        if range_match:

            lower = float(
                range_match.group(1)
            )

            upper = float(
                range_match.group(2)
            )

            if value < lower:
                return "Below Reference Range"

            if value > upper:
                return "Above Reference Range"

            return "Within Reference Range"

        less_than_match = re.search(r"<\s*([-+]?\d*\.?\d+)", reference_range)

        if less_than_match:
            upper = float(less_than_match.group(1))

            if value < upper:
                return "Within Reference Range"

            return "Above Reference Range"

        greater_than_match = re.search(r">\s*([-+]?\d*\.?\d+)", reference_range)
        if greater_than_match:
            lower = float(greater_than_match.group(1))
            if value > lower:
                return "Within Reference Range"

            return "Below Reference Range"

        # -----------------------------------------------------
        # Unable to interpret range
        # -----------------------------------------------------

        return "Reference Range Unavailable"