# from collections import Counter
# from typing import List

# from backend.intelligence.clinical_insight_schema import (
#     ClinicalInsights,
#     ConditionInsight,
#     RecommendationInsight,
#     TestInsight,
# )

# def build_clinical_insights(reports: List, progress) -> ClinicalInsights:

#         insights = ClinicalInsights()

#         insights.active_conditions = _active_conditions(reports)
#         insights.high_risk_conditions = _high_risk_conditions(reports)
#         insights.improving_conditions = _improving_conditions(progress)
#         insights.pending_tests = _pending_tests(reports)

#         insights.frequently_abnormal_tests = (_frequently_abnormal_tests(reports))
#         insights.recurring_recommendations = (_recurring_recommendations(reports))
#         insights.care_gaps = _care_gaps(reports, progress)

#         return insights

# ###############################################################
# # Conditions
# ###############################################################

# def _active_conditions(reports):

#     conditions = set()

#     for report in reports:

#         analysis = report.get("analysis", {})

#         for condition in analysis.get("possible_conditions", []):
#             conditions.add(condition)

#     return [
#         ConditionInsight(
#             name=condition,
#             status="Active",
#         )
#         for condition in sorted(conditions)
#     ]

# def _high_risk_conditions(reports):

#     conditions = set()

#     for report in reports:
#         analysis = report.get("analysis", {})

#         if analysis.get("risk_level") in [
#             "Medium",
#             "High",
#             "Critical",
#         ]:

#             for condition in analysis.get("possible_conditions", []):
#                 conditions.add(condition)

#     return [
#         ConditionInsight(
#             name=condition,
#             status="High Risk",
#         )
#         for condition in sorted(conditions)
#     ]

# def _improving_conditions(progress):

#     # improving = getattr(
#     #     progress,
#     #     "improving_conditions",
#     #     [],
#     # )

#     # return [
#     #     ConditionInsight(
#     #         name=condition,
#     #         status="Improving",
#     #     )
#     #     for condition in improving
#     # ]
#     return []

# ###############################################################
# # Tests
# ###############################################################

# def _pending_tests(reports):

#     pending = []

#     for report in reports:

#         for test in report.get("tests", []):

#             if test.get("status", "").lower() == "pending":

#                 pending.append(
#                     TestInsight(
#                         test_name=test.get("test_name"),
#                         status="Pending",
#                     )
#                 )

#     return pending

# def _frequently_abnormal_tests(reports):

#     counter = Counter()

#     for report in reports:

#         analysis = report.get("analysis", {})

#         for finding in analysis.get("abnormal_findings", []):

#                 if ":" in finding:
#                     test_name = finding.split(":")[0].strip()
#                 else:
#                     test_name = finding

#                 counter[test_name] += 1
            

#     return [
#         TestInsight(
#             test_name=name,
#             status="Recurring Abnormality",
#             note=f"Appeared {count} times",
#         )
#         for name, count in counter.items()
#         if count >= 2
#     ]

# ###############################################################
# # Recommendations
# ###############################################################

# def _recurring_recommendations(reports):

#     counter = Counter()

#     for report in reports:

#         analysis = report.get("analysis", {})

#         for recommendation in analysis.get("recommendations", []):
#                 counter[recommendation] += 1

#     return [
#         RecommendationInsight(
#             recommendation=recommendation,
#             frequency=count,
#         )
#         for recommendation, count in counter.items()
#         if count >= 2
#     ]

# ###############################################################
# # Care Gaps
# ###############################################################

# def _care_gaps(reports, progress):

#     gaps = []

#     pending_tests = _pending_tests(reports)

#     if pending_tests:

#         gaps.append(f"{len(pending_tests)} pending test(s) require follow-up.")

#     if getattr(progress, "overall_trend", "") == "Worsening":

#         gaps.append("Overall health trend is worsening.")

#     if getattr(progress, "overall_trend", "") == "Insufficient Data":

#         gaps.append("Insufficient longitudinal data available.")

#     return gaps

# from collections import Counter
# from typing import List

# from backend.intelligence.clinical_insight_schema import (
#     ClinicalInsights,
#     ConditionInsight,
#     RecommendationInsight,
#     TestInsight,
# )


# def build_clinical_insights(reports: List, progress,) -> ClinicalInsights:
#     """
#     Build deterministic clinical insights from the
#     patient's reports and longitudinal progress.

#     This module does not use an LLM.
#     It only summarizes information that already
#     exists in the structured report/progress data.
#     """

#     if not reports:
#         return ClinicalInsights()

#     return ClinicalInsights(
#         active_conditions=_build_active_conditions(progress),
#         high_risk_conditions=_build_high_risk_conditions(reports),
#         improving_conditions=_build_improving_conditions(progress),
#         pending_tests=_build_pending_tests(reports),
#         frequently_abnormal_tests=_build_frequently_abnormal_tests(reports),
#         recurring_recommendations=_build_recurring_recommendations(reports),
#         care_gaps=_build_care_gaps(reports, progress),
#     )


# # ================================================================
# # CONDITIONS
# # ================================================================

# def _build_active_conditions(progress):
#     """
#     Only conditions that the ProgressTracker has identified
#     as persistent are treated as active.

#     We intentionally DO NOT use:
#         report.analysis.possible_conditions

#     because a possible condition from one report is not
#     automatically an active condition.
#     """

#     persistent_conditions = getattr(progress, "persistent_conditions", [],)

#     results = []
#     seen = set()

#     for condition in persistent_conditions:

#         # ProgressSchema may eventually contain objects instead
#         # of strings, so handle both cases.
#         if isinstance(condition, str):
#             name = condition
#             note = ""
#         else:
#             name = getattr(condition, "condition", str(condition))
#             note = getattr(condition, "note", "")

#         normalized = name.strip().lower()

#         if not normalized or normalized in seen:
#             continue

#         seen.add(normalized)

#         results.append(
#             ConditionInsight(
#                 name=name.strip(),
#                 status="Persistent",
#                 note=note,
#             )
#         )

#     return results


# def _build_high_risk_conditions(reports):
#     """
#     Identify possible conditions associated with reports
#     classified as High or Critical risk.

#     These are still treated as possible conditions,
#     not confirmed diagnoses.
#     """

#     results = []
#     seen = set()

#     for report in reports:

#         analysis = getattr(
#             report,
#             "analysis",
#             None,
#         )

#         if not analysis:
#             continue

#         risk_level = (
#             getattr(
#                 analysis,
#                 "risk_level",
#                 "",
#             )
#             or ""
#         ).strip().lower()

#         if risk_level not in {"high", "critical"}:
#             continue

#         conditions = getattr(
#             analysis,
#             "possible_conditions",
#             [],
#         )

#         for condition in conditions:

#             if not condition:
#                 continue

#             normalized = condition.strip().lower()

#             if normalized in seen:
#                 continue

#             seen.add(normalized)

#             results.append(
#                 ConditionInsight(
#                     name=condition.strip(),
#                     status="Possible - High Risk",
#                     note=(
#                         f"Identified in a {risk_level.capitalize()} "
#                         "risk report."
#                     ),
#                 )
#             )

#     return results


# def _build_improving_conditions(progress):
#     """
#     Use longitudinal progress output rather than trying
#     to infer improvement from a single report.
#     """

#     improving_conditions = getattr(
#         progress,
#         "improving_conditions",
#         [],
#     )

#     results = []
#     seen = set()

#     for condition in improving_conditions:

#         if isinstance(condition, str):
#             name = condition
#             note = ""
#         else:
#             name = getattr(
#                 condition,
#                 "condition",
#                 str(condition),
#             )
#             note = getattr(
#                 condition,
#                 "note",
#                 "",
#             )

#         normalized = name.strip().lower()

#         if not normalized or normalized in seen:
#             continue

#         seen.add(normalized)

#         results.append(
#             ConditionInsight(
#                 name=name.strip(),
#                 status="Improving",
#                 note=note,
#             )
#         )

#     return results


# # ================================================================
# # TESTS
# # ================================================================

# def _build_pending_tests(reports):
#     """
#     Return only tests explicitly marked as Pending.

#     'Unknown' is intentionally NOT treated as Pending.
#     Unknown means we don't have enough information to determine
#     the test's actual state.
#     """

#     results = []
#     seen = set()

#     for report in reports:

#         tests = getattr(
#             report,
#             "tests",
#             [],
#         )

#         for test in tests:

#             status = (
#                 getattr(
#                     test,
#                     "status",
#                     "",
#                 )
#                 or ""
#             ).strip().lower()

#             if status != "pending":
#                 continue

#             test_name = (
#                 getattr(
#                     test,
#                     "test_name",
#                     "",
#                 )
#                 or ""
#             ).strip()

#             if not test_name:
#                 continue

#             normalized = test_name.lower()

#             if normalized in seen:
#                 continue

#             seen.add(normalized)

#             results.append(
#                 TestInsight(
#                     test_name=test_name,
#                     status="Pending",
#                     note="Test result is pending.",
#                 )
#             )

#     return results


# def _build_frequently_abnormal_tests(reports):
#     """
#     Find abnormalities that appear in at least two reports.

#     A single abnormal result is not considered recurring.
#     """

#     occurrences = Counter()
#     display_names = {}

#     for report in reports:

#         analysis = getattr(
#             report,
#             "analysis",
#             None,
#         )

#         if not analysis:
#             continue

#         findings = getattr(
#             analysis,
#             "abnormal_findings",
#             [],
#         )

#         # Avoid counting the same finding twice
#         # inside one report.
#         report_findings = set()

#         for finding in findings:

#             if not finding:
#                 continue

#             finding = finding.strip()

#             if ":" in finding:
#                 test_name = finding.split(
#                     ":",
#                     1,
#                 )[0].strip()
#             else:
#                 test_name = finding

#             normalized = test_name.lower()

#             if normalized in report_findings:
#                 continue

#             report_findings.add(normalized)

#             occurrences[normalized] += 1
#             display_names.setdefault(
#                 normalized,
#                 test_name,
#             )

#     results = []

#     for normalized, count in occurrences.items():

#         if count < 2:
#             continue

#         results.append(
#             TestInsight(
#                 test_name=display_names[normalized],
#                 status="Recurring Abnormality",
#                 note=f"Appeared in {count} reports.",
#             )
#         )

#     return results


# # ================================================================
# # RECOMMENDATIONS
# # ================================================================

# def _build_recurring_recommendations(reports):
#     """
#     Find recommendations that occur across multiple reports.

#     Matching is case-insensitive and whitespace-normalized.
#     """

#     occurrences = Counter()
#     display_names = {}

#     for report in reports:

#         analysis = getattr(
#             report,
#             "analysis",
#             None,
#         )

#         if not analysis:
#             continue

#         recommendations = getattr(
#             analysis,
#             "recommendations",
#             [],
#         )

#         # Count a recommendation only once per report.
#         report_recommendations = set()

#         for recommendation in recommendations:

#             if not recommendation:
#                 continue

#             recommendation = " ".join(
#                 recommendation.strip().split()
#             )

#             normalized = recommendation.lower()

#             if normalized in report_recommendations:
#                 continue

#             report_recommendations.add(normalized)

#             occurrences[normalized] += 1

#             display_names.setdefault(
#                 normalized,
#                 recommendation,
#             )

#     results = []

#     for normalized, count in occurrences.items():

#         if count < 2:
#             continue

#         results.append(
#             RecommendationInsight(
#                 recommendation=display_names[normalized],
#                 frequency=count,
#             )
#         )

#     return results


# # ================================================================
# # CARE GAPS
# # ================================================================

# def _build_care_gaps(reports, progress):
#     """
#     Identify basic data/follow-up gaps.

#     This function intentionally avoids making clinical
#     recommendations or diagnoses.
#     """

#     gaps = []

#     overall_trend = (
#         getattr(
#             progress,
#             "overall_trend",
#             "",
#         )
#         or ""
#     ).strip().lower()

#     if overall_trend == "insufficient data":

#         gaps.append(
#             "Insufficient longitudinal data available."
#         )

#     pending_tests = _build_pending_tests(reports)

#     if pending_tests:

#         gaps.append(
#             f"{len(pending_tests)} pending test(s) "
#             "require follow-up."
#         )

#     return gaps

# from collections import Counter
# from typing import List

# from backend.intelligence.clinical_insight_schema import (
#     ClinicalInsightSchema,
#     ConditionInsight,
#     TestInsight,
# )


# def build_clinical_insights(
#     reports: List,
#     progress,
# ) -> ClinicalInsightSchema:
#     """
#     Build deterministic clinical insights from:

#     1. Individual structured reports
#     2. Longitudinal ProgressSchema

#     No LLM is used here.

#     ProgressSchema is the primary source for longitudinal
#     condition and test-trend information.

#     Individual reports are used to calculate how frequently
#     a test has been abnormal across reports.
#     """
#     print("\n" + "=" * 70)
#     print("DEBUG: CLINICAL INSIGHTS INPUT")
#     print("Reports type:", type(reports))
#     print("Number of reports:", len(reports))

#     for i, report in enumerate(reports):

#         print("\n" + "-" * 60)
#         print(f"REPORT {i + 1}")
#         print("Type:", type(report))
#         print("Report:", report)

#         if hasattr(report, "model_dump"):
#             print("MODEL DUMP:")
#             print(report.model_dump())

#         elif isinstance(report, dict):
#             print("DICT KEYS:")
#             print(report.keys())

#     print("\nPROGRESS TYPE:", type(progress))
#     print("PROGRESS:", progress)

#     if hasattr(progress, "model_dump"):
#         print("PROGRESS DUMP:")
#         print(progress.model_dump())

#     if not reports:
#         return "ClinicalInsights()"
    
#     return ClinicalInsightSchema(
#         active_conditions=_build_active_conditions(progress),
#         high_risk_conditions=_build_high_risk_conditions(
#             reports,
#             progress,
#         ),
#         improving_conditions=_build_improving_conditions(
#             progress,
#         ),
#         frequently_abnormal_tests=_build_frequently_abnormal_tests(
#             reports,
#         ),
#     )


# # ================================================================
# # ACTIVE CONDITIONS
# # ================================================================

# def _build_active_conditions(progress):
#     """
#     Active conditions are conditions identified by the
#     ProgressTracker as persistent.

#     We do NOT use possible_conditions from individual reports
#     because those are report-level possibilities and may not
#     represent persistent conditions.
#     """

#     if progress is None:
#         return []

#     persistent_conditions = getattr(
#         progress,
#         "persistent_conditions",
#         [],
#     ) or []

#     results = []
#     seen = set()

#     for condition in persistent_conditions:

#         name = getattr(
#             condition,
#             "condition",
#             "",
#         )

#         name = (name or "").strip()

#         if not name:
#             continue

#         normalized = name.lower()

#         if normalized in seen:
#             continue

#         seen.add(normalized)

#         results.append(
#             ConditionInsight(
#                 name=name,
#                 status="Persistent",
#                 note=(
#                     "Condition identified as persistent "
#                     "across the longitudinal timeline."
#                 ),
#             )
#         )

#     return results


# # ================================================================
# # HIGH-RISK / CONCERNING CONDITIONS
# # ================================================================

# def _build_high_risk_conditions(
#     reports,
#     progress,
# ):
#     """
#     Identify clinically concerning findings from longitudinal
#     progress and high-risk reports.

#     This does not claim that a condition is a confirmed diagnosis.

#     Sources:

#     1. New conditions from ProgressSchema
#     2. Worsening test trends from ProgressSchema
#     3. Possible conditions from High/Critical risk reports
#     """

#     results = []
#     seen = set()

#     # ------------------------------------------------------------
#     # 1. New conditions from ProgressSchema
#     # ------------------------------------------------------------

#     if progress is not None:

#         new_conditions = getattr(
#             progress,
#             "new_conditions",
#             [],
#         ) or []

#         for condition in new_conditions:

#             name = getattr(
#                 condition,
#                 "condition",
#                 "",
#             )

#             name = (name or "").strip()

#             if not name:
#                 continue

#             normalized = name.lower()

#             if normalized in seen:
#                 continue

#             seen.add(normalized)

#             first_seen = getattr(
#                 condition,
#                 "first_seen",
#                 None,
#             )

#             note = (
#                 "New condition identified in the "
#                 "longitudinal timeline."
#             )

#             if first_seen:
#                 note += f" First seen on {first_seen}."

#             results.append(
#                 ConditionInsight(
#                     name=name,
#                     status="New",
#                     note=note,
#                 )
#             )

#     # ------------------------------------------------------------
#     # 2. Worsening test trends
#     # ------------------------------------------------------------

#     if progress is not None:

#         test_trends = getattr(
#             progress,
#             "test_trends",
#             [],
#         ) or []

#         for trend in test_trends:

#             trend_type = (
#                 getattr(
#                     trend,
#                     "trend",
#                     "",
#                 )
#                 or ""
#             ).strip()

#             if trend_type != "Worsened":
#                 continue

#             test_name = (
#                 getattr(
#                     trend,
#                     "test_name",
#                     "",
#                 )
#                 or ""
#             ).strip()

#             note = (
#                 getattr(
#                     trend,
#                     "note",
#                     "",
#                 )
#                 or ""
#             ).strip()

#             if not test_name:
#                 continue

#             normalized = test_name.lower()

#             if normalized in seen:
#                 continue

#             seen.add(normalized)

#             results.append(
#                 ConditionInsight(
#                     name=test_name,
#                     status="Worsening",
#                     note=note,
#                 )
#             )

#     # ------------------------------------------------------------
#     # 3. High/Critical risk reports
#     # ------------------------------------------------------------

#     for report in reports or []:

#         analysis = getattr(
#             report,
#             "analysis",
#             None,
#         )

#         if not analysis:
#             continue

#         risk_level = (
#             getattr(
#                 analysis,
#                 "risk_level",
#                 "",
#             )
#             or ""
#         ).strip().lower()

#         if risk_level not in {
#             "high",
#             "critical",
#         }:
#             continue

#         possible_conditions = getattr(
#             analysis,
#             "possible_conditions",
#             [],
#         ) or []

#         for condition in possible_conditions:

#             condition = (condition or "").strip()

#             if not condition:
#                 continue

#             normalized = condition.lower()

#             if normalized in seen:
#                 continue

#             seen.add(normalized)

#             results.append(
#                 ConditionInsight(
#                     name=condition,
#                     status="Worsening",
#                     note=(
#                         f"Associated with a "
#                         f"{risk_level.capitalize()}-risk report."
#                     ),
#                 )
#             )

#     return results


# # ================================================================
# # IMPROVING CONDITIONS / FINDINGS
# # ================================================================

# def _build_improving_conditions(progress):
#     """
#     Identify improving findings from ProgressSchema.

#     Important:
#     We only label the specific finding/test as improving.

#     We do NOT infer that an entire disease has improved simply
#     because one laboratory marker improved.
#     """

#     if progress is None:
#         return []

#     test_trends = getattr(
#         progress,
#         "test_trends",
#         [],
#     ) or []

#     results = []
#     seen = set()

#     for trend in test_trends:

#         trend_type = (
#             getattr(
#                 trend,
#                 "trend",
#                 "",
#             )
#             or ""
#         ).strip()

#         if trend_type != "Improved":
#             continue

#         test_name = (
#             getattr(
#                 trend,
#                 "test_name",
#                 "",
#             )
#             or ""
#         ).strip()

#         note = (
#             getattr(
#                 trend,
#                 "note",
#                 "",
#             )
#             or ""
#         ).strip()

#         if not test_name:
#             continue

#         normalized = test_name.lower()

#         if normalized in seen:
#             continue

#         seen.add(normalized)

#         results.append(
#             ConditionInsight(
#                 name=test_name,
#                 status="Improving",
#                 note=note,
#             )
#         )

#     return results


# # ================================================================
# # FREQUENTLY ABNORMAL TESTS
# # ================================================================

# def _build_frequently_abnormal_tests(reports):
#     """
#     Identify tests that were abnormal in multiple reports.

#     Example:

#         HbA1c abnormal in 3/3 reports

#     becomes:

#         {
#             "test_name": "HbA1c",
#             "abnormal_report_count": 3,
#             "total_report_count": 3
#         }

#     We count a test at most once per report.
#     """

#     if not reports:
#         return []

#     total_report_count = len(reports)

#     abnormal_counts = Counter()
#     display_names = {}

#     for report in reports:

#         analysis = getattr(
#             report,
#             "analysis",
#             None,
#         )
#         print("\n" + "=" * 60)
#         print("DEBUG REPORT")
#         print("Report ID:", getattr(report, "report_id", None))
#         print("Analysis type:", type(analysis))
#         print("Analysis:", analysis)
#         if not analysis:
#             continue

#         abnormal_findings = getattr(
#             analysis,
#             "abnormal_findings",
#             [],
#         ) or []

#         # --------------------------------------------------------
#         # Prevent duplicate counting inside the same report.
#         # --------------------------------------------------------

#         report_tests = set()

#         for finding in abnormal_findings:

#             if not finding:
#                 continue

#             finding = finding.strip()

#             # Expected format:
#             #
#             # HbA1c: 6.90% (High)
#             #
#             # Extract:
#             #
#             # HbA1c
#             #
#             if ":" in finding:

#                 test_name = finding.split(
#                     ":",
#                     1,
#                 )[0].strip()

#             else:

#                 test_name = finding.strip()

#             if not test_name:
#                 continue

#             normalized = test_name.lower()

#             if normalized in report_tests:
#                 continue

#             report_tests.add(normalized)

#             abnormal_counts[normalized] += 1

#             display_names.setdefault(
#                 normalized,
#                 test_name,
#             )

#     results = []

#     for normalized, count in abnormal_counts.items():

#         # Only include tests abnormal in at least
#         # two reports.
#         if count < 2:
#             continue

#         results.append(
#             TestInsight(
#                 test_name=display_names[normalized],
#                 abnormal_report_count=count,
#                 total_report_count=total_report_count,
#                 note=(
#                     f"Abnormal in {count} of "
#                     f"{total_report_count} reports."
#                 ),
#             )
#         )

#     return results


from collections import Counter
from typing import List

from backend.intelligence.clinical_insight_schema import (
    ClinicalInsightSchema,
    ConditionInsight,
    TestInsight,
)


def build_clinical_insights(
    reports: List[dict],
    progress,
) -> ClinicalInsightSchema:
    """
    Build deterministic clinical insights from structured
    report dictionaries and longitudinal ProgressSchema.

    No LLM is used in this module.

    Expected report structure:

    {
        "report_id": ...,
        "report_type": ...,
        "report_date": ...,
        "lab_name": ...,
        "created_at": ...,
        "tests": [...],
        "analysis": {
            "abnormal_findings": [...],
            "possible_conditions": [...],
            "recommendations": [...],
            "follow_up_tests": [...],
            "risk_level": ...
        }
    }
    """

    if not reports:
        return ClinicalInsightSchema(
            active_conditions=[],
            high_risk_conditions=[],
            improving_conditions=[],
            frequently_abnormal_tests=[],
        )

    return ClinicalInsightSchema(
        active_conditions=_build_active_conditions(progress),
        high_risk_conditions=_build_high_risk_conditions(reports),
        improving_conditions=_build_improving_conditions(progress),
        frequently_abnormal_tests=_build_frequently_abnormal_tests(
            reports
        ),
    )


# ================================================================
# HELPERS
# ================================================================

def _get_report_analysis(report: dict) -> dict:
    """
    Retrieve the analysis section from a report dictionary.

    Returns an empty dictionary if analysis is missing or invalid.
    """

    if not isinstance(report, dict):
        return {}

    analysis = report.get("analysis")

    if not isinstance(analysis, dict):
        return {}

    return analysis


def _normalize_text(value) -> str:
    """
    Normalize text for case-insensitive comparisons.
    """

    if value is None:
        return ""

    return " ".join(str(value).strip().lower().split())


# ================================================================
# ACTIVE CONDITIONS
# ================================================================

def _build_active_conditions(progress) -> list[ConditionInsight]:
    """
    Active conditions are conditions identified as persistent
    across the longitudinal timeline.

    Source:
        progress.persistent_conditions

    We intentionally do NOT use possible_conditions from
    individual reports because a possible condition in one
    report is not automatically an active/persistent condition.
    """

    persistent_conditions = getattr(
        progress,
        "persistent_conditions",
        [],
    )

    results = []
    seen = set()

    for condition in persistent_conditions:

        if isinstance(condition, str):
            name = condition
        else:
            name = getattr(
                condition,
                "condition",
                "",
            )

        name = str(name).strip()

        if not name:
            continue

        normalized = _normalize_text(name)

        if normalized in seen:
            continue

        seen.add(normalized)

        results.append(
            ConditionInsight(
                name=name,
                status="Persistent",
                note=(
                    "Condition identified as persistent "
                    "across the longitudinal timeline."
                ),
            )
        )

    return results


# ================================================================
# HIGH-RISK CONDITIONS
# ================================================================

def _build_high_risk_conditions(
    reports: List[dict],
) -> list[ConditionInsight]:
    """
    Identify possible conditions from reports whose risk level
    is High or Critical.

    Important:
        These remain possible conditions.
        They are NOT converted into confirmed diagnoses.

    We only use report-level risk information here.

    We DO NOT use:
        - test trends
        - hsCRP
        - RBCs
        - other individual laboratory tests

    because those belong to test-level insights, not conditions.
    """

    results = []
    seen = set()

    for report in reports:

        analysis = _get_report_analysis(report)

        risk_level = _normalize_text(
            analysis.get("risk_level")
        )

        if risk_level not in {"high", "critical"}:
            continue

        conditions = analysis.get(
            "possible_conditions",
            [],
        )

        if not isinstance(conditions, list):
            continue

        for condition in conditions:

            if not condition:
                continue

            name = str(condition).strip()

            if not name:
                continue

            normalized = _normalize_text(name)

            if normalized in seen:
                continue

            seen.add(normalized)

            results.append(
                ConditionInsight(
                    name=name,
                    status="Worsening",
                    note=(
                        f"Possible condition identified in a "
                        f"{risk_level.capitalize()} risk report."
                    ),
                )
            )

    return results


# ================================================================
# IMPROVING CONDITIONS
# ================================================================

def _build_improving_conditions(progress) -> list[ConditionInsight]:
    """
    Identify conditions that are explicitly described as improving
    at the condition level.

    Current ProgressSchema does not contain an
    'improving_conditions' field.

    Therefore, this function intentionally returns an empty list
    rather than incorrectly converting improving laboratory tests
    such as Haemoglobin or HDL into conditions.

    This is important because:

        Haemoglobin improving != Anemia resolved

        HDL improving != Dyslipidemia resolved

    Those are test-level improvements and belong in
    test_trends / frequently_abnormal_tests.
    """

    # ProgressSchema currently does not provide
    # condition-level improving_conditions.

    return []


# ================================================================
# FREQUENTLY ABNORMAL TESTS
# ================================================================

def _build_frequently_abnormal_tests(
    reports: List[dict],
) -> list[TestInsight]:
    """
    Identify tests that are abnormal in multiple reports.

    Uses:

        analysis["abnormal_findings"]

    to determine abnormality.

    Uses:

        report["tests"]

    to determine how many reports contained the test.

    Example:

        HbA1c abnormal in 3 reports
        HbA1c present in 3 reports

    Result:

        {
            "test_name": "HbA1c",
            "abnormal_report_count": 3,
            "total_report_count": 3,
            ...
        }

    A test is considered frequently abnormal only when it is
    abnormal in at least two reports.
    """

    abnormal_counts = Counter()
    total_counts = Counter()
    display_names = {}

    # ------------------------------------------------------------
    # 1. Count test presence across reports
    # ------------------------------------------------------------

    for report in reports:

        tests = report.get("tests", [])

        if not isinstance(tests, list):
            continue

        report_tests = set()

        for test in tests:

            if not isinstance(test, dict):
                continue

            test_name = (
                test.get("test_name")
                or ""
            ).strip()

            if not test_name:
                continue

            normalized = _normalize_text(test_name)

            if normalized in report_tests:
                continue

            report_tests.add(normalized)

            total_counts[normalized] += 1

            display_names.setdefault(
                normalized,
                test_name,
            )

    # ------------------------------------------------------------
    # 2. Count abnormal occurrences across reports
    # ------------------------------------------------------------

    for report in reports:

        analysis = _get_report_analysis(report)

        findings = analysis.get(
            "abnormal_findings",
            [],
        )

        if not isinstance(findings, list):
            continue

        report_abnormal_tests = set()

        for finding in findings:

            if not finding:
                continue

            finding = str(finding).strip()

            if not finding:
                continue

            # Expected examples:
            #
            # HbA1c: 6.90% (High)
            # Haemoglobin (HB): 11.4 g/dl (Low)
            # MCV: 67.5 FL (Low)

            if ":" in finding:

                test_name = finding.split(
                    ":",
                    1,
                )[0].strip()

            else:
                test_name = finding.strip()

            if not test_name:
                continue

            normalized = _normalize_text(test_name)

            # Avoid counting the same test twice
            # within the same report.
            if normalized in report_abnormal_tests:
                continue

            report_abnormal_tests.add(normalized)

            abnormal_counts[normalized] += 1

            display_names.setdefault(
                normalized,
                test_name,
            )

    # ------------------------------------------------------------
    # 3. Build final insights
    # ------------------------------------------------------------

    results = []

    for normalized, abnormal_count in abnormal_counts.items():

        # A single abnormal report is not considered
        # a frequently abnormal test.
        if abnormal_count < 2:
            continue

        total_report_count = total_counts.get(
            normalized,
            abnormal_count,
        )

        results.append(
            TestInsight(
                test_name=display_names[normalized],
                abnormal_report_count=abnormal_count,
                total_report_count=total_report_count,
                note=(
                    f"Abnormal in {abnormal_count} of "
                    f"{total_report_count} reports."
                ),
            )
        )

    # Stable ordering makes output easier to test/debug.
    results.sort(
        key=lambda item: (
            -item.abnormal_report_count,
            item.test_name.lower(),
        )
    )

    return results

