# from typing import List, Dict, Any
# import re

# class ComparisonEngine:

#     def compare_test(self,reports: List[Dict[str, Any]],test_name: str) -> Dict[str, Any]:

#         measurements = []
#         for report in reports:
#             report_date = report.get("report_date")
#             for test in report.get("tests", []):
#                 current_test_name = test.get("test_name", "")
#                 # Match the requested test against the report test name.
#                 if not self._test_name_matches(test_name, current_test_name):
#                     continue

#                 value = self._parse_numeric(test.get("result"))

#                 if value is None:
#                     continue
#                 measurements.append(
#                     {
#                         "date": report_date,
#                         "value": value,
#                         "unit": test.get("unit", ""),
#                         "reference_range": test.get(
#                             "normal_range",
#                             ""
#                         ),
#                     }
#                 )
#                 # Only one matching test per report is needed.
#                 break

#         # Sort chronologically
#         measurements.sort(key=lambda x: x["date"])

#         # Not enough data
#         if not measurements:
#             return {
#                 "test_name": test_name,
#                 "measurements": [],
#                 "changes": [],
#                 "trend": "Insufficient Data",
#             }

#         # Calculate changes between consecutive reports
#         changes = []
#         for previous, current in zip(measurements, measurements[1:]):
#             change = (current["value"] - previous["value"])
#             if change > 0:
#                 direction = "increased"
#             elif change < 0:
#                 direction = "decreased"
#             else:
#                 direction = "stable"

#             changes.append(
#                 {
#                     "from_date": previous["date"],
#                     "to_date": current["date"],
#                     "from_value": previous["value"],
#                     "to_value": current["value"],
#                     "change": round(change, 4),
#                     "direction": direction,
#                 }
#             )

#         trend = self._determine_trend(measurements)
#         return {
#             "test_name": test_name,
#             "measurements": measurements,
#             "changes": changes,
#             "trend": trend,
#         }

#     # ---------------------------------------------------------
#     # Test-name matching
#     # ---------------------------------------------------------

#     @staticmethod
#     def _test_name_matches(requested_name: str, actual_name: str) -> bool:

#         requested = ComparisonEngine._normalize(requested_name)
#         actual = ComparisonEngine._normalize(actual_name)

#         # 1. Exact match
#         if requested == actual:
#             return True

#         # 2. Token-based matching
#         requested_tokens = set(requested.split())

#         actual_tokens = set(actual.split())

#         if not requested_tokens:
#             return False

#         common_tokens = (requested_tokens & actual_tokens)
#         meaningful_tokens = {token for token in requested_tokens if len(token) > 1}

#         if meaningful_tokens and (len(common_tokens) / len(meaningful_tokens) >= 0.5):
#             return True

#         return False

#     # ---------------------------------------------------------
#     # Normalization
#     # ---------------------------------------------------------

#     @staticmethod
#     def _normalize(value: str) -> str:

#         value = str(value).strip().casefold()

#         # Replace punctuation with spaces
#         value = re.sub(r"[^a-z0-9]+"," ",value)

#         # Remove extra whitespace
#         value = re.sub(r"\s+"," ",value)
#         return value.strip()

#     # ---------------------------------------------------------
#     # Numeric parsing
#     # ---------------------------------------------------------

#     @staticmethod
#     def _parse_numeric(value):

#         if value is None:
#             return None

#         if isinstance(value,(int, float)):
#             return float(value)

#         value = str(value).strip()

#         if not value:
#             return None

#         # Remove commas
#         value = value.replace(",", "")

#         # Direct numeric value
#         try:
#             return float(value)
#         except ValueError:
#             pass

#         match = re.search(r"[-+]?\d*\.?\d+",value)
#         if match:
#             try:
#                 return float(match.group())
#             except ValueError:
#                 return None

#         return None

#     # ---------------------------------------------------------
#     # Trend calculation
#     # ---------------------------------------------------------

#     @staticmethod
#     def _determine_trend(measurements):

#         if len(measurements) < 2:
#             return "Insufficient Data"

#         values = [item["value"] for item in measurements]

#         increases = 0
#         decreases = 0
#         for previous, current in zip(values, values[1:],):
#             if current > previous:
#                 increases += 1

#             elif current < previous:
#                 decreases += 1

#         if increases and decreases:
#             return "Fluctuating"
#         if increases:
#             return "Increasing"
#         if decreases:
#             return "Decreasing"
#         return "Stable"


from typing import List, Dict, Any
import re
from datetime import date


class ComparisonEngine:

    def compare_test(
        self,
        reports: List[Dict[str, Any]],
        test_name: str
    ) -> Dict[str, Any]:

        measurements = []

        for report in reports:

            report_date = report.get("report_date")

            if not report_date:
                continue

            for test in report.get("tests", []):

                current_test_name = test.get("test_name", "")

                # Match the requested test against the
                # actual test name stored in the report.
                if not self._test_name_matches(
                    test_name,
                    current_test_name
                ):
                    continue

                raw_value = test.get("result")

                value = self._parse_numeric(raw_value)

                # Skip values that cannot safely be treated
                # as a single numeric measurement.
                if value is None:
                    continue

                measurements.append(
                    {
                        "date": report_date,
                        "value": value,
                        "unit": test.get("unit", ""),
                        "reference_range": test.get(
                            "normal_range",
                            ""
                        ),
                    }
                )

                # Only one matching test per report is needed.
                break

        # ---------------------------------------------------------
        # Sort chronologically
        # ---------------------------------------------------------

        measurements.sort(
            key=lambda item: self._parse_date(item["date"])
        )

        # ---------------------------------------------------------
        # Not enough usable data
        # ---------------------------------------------------------

        if not measurements:
            return {
                "test_name": test_name,
                "measurements": [],
                "changes": [],
                "trend": "Insufficient Data",
            }

        # ---------------------------------------------------------
        # Calculate changes between consecutive reports
        # ---------------------------------------------------------

        changes = []

        for previous, current in zip(
            measurements,
            measurements[1:]
        ):

            change = (
                current["value"]
                - previous["value"]
            )

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
        # Determine overall mathematical trend
        # ---------------------------------------------------------

        trend = self._determine_trend(measurements)

        return {
            "test_name": test_name,
            "measurements": measurements,
            "changes": changes,
            "trend": trend,
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
    def _test_name_matches(
        requested_name: str,
        actual_name: str
    ) -> bool:

        requested = ComparisonEngine._normalize(
            requested_name
        )

        actual = ComparisonEngine._normalize(
            actual_name
        )

        # -----------------------------------------------------
        # Exact match
        # -----------------------------------------------------

        if requested == actual:
            return True

        # -----------------------------------------------------
        # Token-based matching
        # -----------------------------------------------------

        requested_tokens = set(
            requested.split()
        )

        actual_tokens = set(
            actual.split()
        )

        if not requested_tokens:
            return False

        common_tokens = (
            requested_tokens & actual_tokens
        )

        meaningful_tokens = {
            token
            for token in requested_tokens
            if len(token) > 1
        }

        if (
            meaningful_tokens
            and
            len(common_tokens)
            /
            len(meaningful_tokens)
            >= 0.5
        ):
            return True

        return False

    # =========================================================
    # NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize(value: str) -> str:

        value = str(value).strip().casefold()

        # Replace punctuation with spaces
        value = re.sub(
            r"[^a-z0-9]+",
            " ",
            value
        )

        # Remove extra whitespace
        value = re.sub(
            r"\s+",
            " ",
            value
        )

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

        # -----------------------------------------------------
        # Avoid treating ranges such as "1-2 /HPF"
        # as the single numeric value 1.
        # -----------------------------------------------------

        if re.search(
            r"\d+\s*-\s*\d+",
            value
        ):
            return None

        # Remove commas
        value = value.replace(",", "")

        # Direct numeric value
        try:
            return float(value)

        except ValueError:
            pass

        # Extract a single numeric value
        match = re.fullmatch(
            r"\s*[-+]?\d*\.?\d+\s*.*",
            value
        )

        if match:

            number_match = re.search(
                r"[-+]?\d*\.?\d+",
                value
            )

            if number_match:

                try:
                    return float(
                        number_match.group()
                    )

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

        values = [
            item["value"]
            for item in measurements
        ]

        increases = 0
        decreases = 0

        for previous, current in zip(
            values,
            values[1:]
        ):

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