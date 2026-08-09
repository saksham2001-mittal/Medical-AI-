# from textwrap import dedent


# def build_progress_prompt(timeline: str, output_schema: str) -> str:
#     """
#     Prompt for longitudinal patient progress analysis.
#     """

#     return dedent(
#         f"""
#     You are an Experienced Clinical Physician specialized in creating a complete longitudinal patient care.

#     Your task is to analyze the patient's health progression across multiple medical reports arranged in chronological order.

#     The reports have already been processed and validated.
#     DO NOT extract information again.
#     Instead, identify how the patient's overall health has changed over time.

#     ==============================
#     YOUR OBJECTIVE
#     ==============================

#     Review the complete patient timeline and determine:

#     1. Overall health trend
#     2. Changes in risk level
#     3. Conditions that have resolved
#     4. Newly developed conditions
#     5. Persistent conditions
#     6. Progress of laboratory tests over time
#     7. Important clinical changes
#     8. Recommended follow-up actions

#     Always reason across ALL reports together.
#     Do NOT treat each report independently.

#     ==============================
#     OVERALL TREND
#     ==============================

#     Choose exactly ONE:

#     - Improving
#     - Stable
#     - Worsening
#     - Mixed
#     - Insufficient Data

#     Definitions

#     Improving
#     - fewer abnormalities
#     - lower risk
#     - improving laboratory values
#     - fewer conditions

#     Stable
#     - little or no change
#     - similar findings across reports

#     Worsening
#     - increasing abnormalities
#     - higher risk
#     - worsening laboratory values
#     - new significant diseases

#     Mixed
#     - some findings improved while others worsened

#     Insufficient Data
#     - not enough information to determine progression

#     ==============================
#     RISK HISTORY
#     ==============================

#     For each report provide

#     - report date
#     - risk level

#     Keep chronological order.

#     ==============================
#     CONDITION ANALYSIS
#     ==============================

#     Resolved Conditions

#     Conditions present previously but no longer reported.

#     New Conditions

#     Conditions appearing for the first time.

#     Persistent Conditions

#     Conditions continuing across multiple reports.

#     Only include medically meaningful conditions.

#     ==============================
#     TEST TRENDS
#     ==============================

#     Compare repeated laboratory tests across reports.    

#     For individual test trends:

#     Improved
#     - The test shows an overall clinically meaningful improvement over time.

#     Worsened
#     - The test shows an overall clinically meaningful deterioration over time.

#     Stable
#     - Values remain broadly similar over time without meaningful directional change.

#     Mixed
#     - The value improves during one period but worsens during another period.
#     - Use this when the trajectory changes direction.

#     Insufficient Data
#     - Only one usable value exists, or there is insufficient information to determine a trend.

#     ==============================
#     IMPORTANT CHANGES
#     ==============================

#     Include clinically important changes such as

#     - new diagnosis
#     - resolved diagnosis
#     - surgery
#     - hospitalization
#     - major medication changes
#     - important laboratory deterioration
#     - major laboratory improvement

#     Do NOT include trivial wording differences.

#     ==============================
#     FOLLOW-UP
#     ==============================

#     Recommend follow-up based on the patient's journey.

#     Examples

#     - Repeat HbA1c in 3 months
#     - Lipid profile follow-up
#     - Cardiology consultation
#     - Continue current treatment

#     Only recommend actions supported by the timeline.

#     ==============================
#     HEALTH SUMMARY
#     ==============================

#     Write 3-6 concise sentences summarizing

#     - overall progression
#     - current health status
#     - major improvements
#     - major concerns

#     This should read like a physician's longitudinal assessment.

#     ==============================
#     IMPORTANT RULES
#     ==============================

#     DO NOT ASSUME THE FOLLOWING IF NOT PRESENT:

#     - invent diseases
#     - invent laboratory values
#     - invent dates
#     - invent medications
#     - contradict the reports

#     Base every conclusion only on the provided timeline.

#     If evidence is insufficient,
#     return "Insufficient Data".

#     ==============================
#     TIMELINE
#     ==============================

#     {timeline}

#     ==============================
#     OUTPUT FORMAT
#     ==============================

#     Return ONLY a JSON object matching the following exact structure.

#     IMPORTANT:
#     - Do NOT create a "condition_analysis" object.
#     - resolved_conditions MUST be a top-level field.
#     - new_conditions MUST be a top-level field.
#     - persistent_conditions MUST be a top-level field.
#     - important_changes MUST be a list of strings.
#     - recommended_follow_up MUST be a list of strings.
#     - test_trends.trend MUST be one of:
#     "Improved", "Worsened", "Stable", "Mixed", "Insufficient Data".

#     The JSON structure MUST be:

#     {{
#         "overall_trend": "Improved | Worsened | Stable | Mixed | Insufficient Data",

#         "health_summary": "string",

#         "risk_history": [
#             {{
#                 "report_date": "YYYY-MM-DD",
#                 "risk_level": "Low | Medium | High | Critical"
#             }}
#         ],

#         "resolved_conditions": [
#             {{
#                 "condition": "string",
#                 "first_seen": "YYYY-MM-DD",
#                 "last_seen": "YYYY-MM-DD"
#             }}
#         ],

#         "new_conditions": [
#             {{
#                 "condition": "string",
#                 "first_seen": "YYYY-MM-DD",
#                 "last_seen": "YYYY-MM-DD"
#             }}
#         ],

#         "persistent_conditions": [
#             {{
#                 "condition": "string",
#                 "first_seen": "YYYY-MM-DD",
#                 "last_seen": "YYYY-MM-DD"
#             }}
#         ],

#         "test_trends": [
#             {{
#                 "test_name": "string",
#                 "trend": "Improved | Worsened | Stable | Mixed | Insufficient Data",
#                 "note": "string"
#             }}
#         ],

#         "important_changes": [
#             "string"
#         ],

#         "recommended_follow_up": [
#             "string"
#         ]
#     }}

#     Do NOT add extra fields.
#     Do NOT nest resolved_conditions, new_conditions, or persistent_conditions inside another object.
#     Return ONLY valid JSON.
#     """
#         # {output_schema}

#         # Return ONLY valid JSON.
#         # """
# )

from textwrap import dedent


def build_progress_prompt(timeline: str, output_schema: str) -> str:
    """
    Prompt for longitudinal patient progress analysis.

    The LLM must analyze all available reports chronologically
    and return output matching ProgressSchema exactly.
    """

    return dedent(
        f"""
        You are an experienced clinical physician specializing in
        longitudinal patient health assessment.

        Your task is to analyze the patient's health progression across
        multiple medical reports arranged in chronological order.

        The reports have already been processed and validated.

        DO NOT extract information again.
        DO NOT invent missing information.
        DO NOT treat reports independently.

        Instead, compare ALL reports together and determine how the
        patient's health has changed over time.

        ============================================================
        OBJECTIVE
        ============================================================

        Analyze:

        1. Overall health trend
        2. Changes in risk level
        3. Resolved conditions
        4. Newly developed conditions
        5. Persistent conditions
        6. Laboratory test trends
        7. Important clinical changes
        8. Recommended follow-up actions
        9. Overall longitudinal health summary

        Always reason across the COMPLETE timeline.

        ============================================================
        TREND DEFINITIONS
        ============================================================

        Use the following trend vocabulary consistently for BOTH:

        1. overall_trend
        2. test_trends[].trend

        Allowed values:

        - Improved
        - Worsened
        - Stable
        - Fluctuating
        - Insufficient Data

        Definitions:

        Improved
        - The available evidence shows a meaningful movement toward
        better health or a more favorable clinical state.

        Worsened
        - The available evidence shows a meaningful movement toward
        poorer health or a less favorable clinical state.

        Stable
        - Findings remain broadly unchanged over time with no meaningful
        directional change.

        Fluctuating
        - The same health measure or clinical area shows meaningful
        movement in both directions over time.
        - For example:
            6.9 → 6.2 → 6.7
        represents improvement followed by deterioration.

        Insufficient Data
        - There is insufficient longitudinal evidence to determine
        a meaningful direction of change.

        IMPORTANT:
        Do not classify something as Fluctuating merely because values
        change slightly.

        A trend should be considered Fluctuating only when there is
        meaningful directional change supported by the available data.

        ============================================================
        OVERALL TREND
        ============================================================

        Determine the patient's overall longitudinal health trend.

        Use ONLY the trend categories defined in TREND DEFINITIONS.

        Consider ALL clinically meaningful findings together, including:

        - conditions
        - risk levels
        - laboratory trends
        - newly developed problems
        - resolved problems
        - persistent abnormalities

        Do not determine the overall trend from a single laboratory test.
        
        ============================================================
        RISK HISTORY
        ============================================================

        For every available report provide:

        - report_date
        - risk_level

        Keep reports in chronological order.

        Use only these risk levels:

        - Low
        - Medium
        - High
        - Critical

        Do not invent a risk level if it is not supported by the timeline.

        ============================================================
        CONDITION ANALYSIS
        ============================================================

        Resolved Conditions

        Include conditions that were previously documented but are no
        longer documented in later reports.

        New Conditions

        Include clinically meaningful conditions that appear for the
        first time in the timeline.

        Persistent Conditions

        Include clinically meaningful conditions that continue across
        multiple reports.

        For every condition provide:

        - condition
        - first_seen
        - last_seen

        Do not include trivial wording differences.

        IMPORTANT:
        These fields MUST be returned as TOP-LEVEL JSON fields.

        Do NOT create a nested "condition_analysis" object.

        ============================================================
        TEST TRENDS
        ============================================================

        Compare repeated laboratory tests across reports.

        For each repeated test provide:

        - test_name
        - trend
        - note

        Use ONLY the trend categories defined in TREND DEFINITIONS.

        For a single measurement or insufficient longitudinal evidence,
        use:

        "Insufficient Data"

        Do not assume that an increase or decrease is automatically
        better or worse.

        Interpret the direction according to:

        - the clinical meaning of the test
        - the provided reference range
        - the reported status
        - the longitudinal context

        Never invent laboratory values.

        ============================================================
        IMPORTANT CHANGES
        ============================================================

        Include only clinically meaningful longitudinal changes.

        Examples:

        - new diagnosis
        - resolved diagnosis
        - new clinically significant abnormality
        - important laboratory deterioration
        - important laboratory improvement
        - major medication change
        - surgery
        - hospitalization

        Do NOT include trivial wording differences.

        IMPORTANT:
        "important_changes" MUST be a list of STRINGS.

        Correct:

        [
            "hsCRP increased significantly in 2026.",
            "Urinary RBCs increased over successive reports."
        ]

        Incorrect:

        [
            {{"condition": "hsCRP increased significantly in 2026."}}
        ]

        ============================================================
        RECOMMENDED FOLLOW-UP
        ============================================================

        Recommend follow-up actions supported by the patient's timeline.

        Examples:

        - Repeat HbA1c monitoring.
        - Repeat lipid profile.
        - Consider renal evaluation for persistent hematuria.
        - Continue monitoring abnormal laboratory markers.

        Do not recommend actions unsupported by the available information.

        IMPORTANT:
        "recommended_follow_up" MUST be a list of STRINGS.

        Correct:

        [
            "Repeat HbA1c monitoring.",
            "Evaluate persistent hematuria."
        ]

        Incorrect:

        [
            {{"condition": "Repeat HbA1c monitoring."}}
        ]

        ============================================================
        HEALTH SUMMARY
        ============================================================

        Write 3-6 concise sentences describing:

        - overall longitudinal progression
        - current health status
        - major improvements
        - major concerns

        The summary should reflect the complete timeline.

        ============================================================
        STRICT EVIDENCE RULES
        ============================================================

        Base every conclusion ONLY on the supplied timeline.

        DO NOT:

        - invent diseases
        - invent laboratory values
        - invent dates
        - invent medications
        - invent procedures
        - invent hospitalizations
        - assume a diagnosis from a single abnormal value
        - contradict the reports

        If evidence is insufficient, use:

        "Insufficient Data"

        or return an empty list where appropriate.

        ============================================================
        STRICT OUTPUT CONTRACT
        ============================================================

        You MUST return exactly these TOP-LEVEL fields:

        {{
            "overall_trend": "...",
            "health_summary": "...",
            "risk_history": [],
            "resolved_conditions": [],
            "new_conditions": [],
            "persistent_conditions": [],
            "test_trends": [],
            "important_changes": [],
            "recommended_follow_up": []
        }}

        DO NOT create:

        - "condition_analysis"
        - "clinical_analysis"
        - "summary"
        - "conditions"
        - any other additional wrapper object

        The following fields MUST be lists of strings:

        "important_changes"
        "recommended_follow_up"

        The following fields MUST contain objects matching their
        corresponding schema:

        "risk_history"
        "resolved_conditions"
        "new_conditions"
        "persistent_conditions"
        "test_trends"

        Do not add extra fields.

        ============================================================
        TIMELINE
        ============================================================

        {timeline}

        ============================================================
        OUTPUT SCHEMA
        ============================================================

        {output_schema}

        ============================================================
        FINAL INSTRUCTION
        ============================================================

        Return ONLY valid JSON.

        The JSON structure MUST match the supplied output schema exactly.
    """
    )