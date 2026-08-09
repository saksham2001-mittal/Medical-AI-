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

    Your task is to extract structured information from OCR text of pathology, laboratory and diagnostic reports.

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

    Extract EVERY laboratory test result.
    For every test extract:

    - test_name
    - result
    - unit
    - normal_range
    - status
    - test_date
    
    -----------------------------------------
    Scenario Based Rules
    -----------------------------------------
        -----------------------------------------
        RULE 1
        -----------------------------------------

        If the report contains an ACTUAL laboratory value:

        For Example:
            HbA1c
            8.2 %
            Reference: 4.0 - 5.6
            20/10/2023

        Return

        {{
            "test_name":"HbA1c",
            "result":"8.2",
            "unit":"%",
            "normal_range":"4.0 - 5.6",
            "status":"High",
            "test_date":"2023-10-20"
        }}

        -----------------------------------------
        RULE 2
        -----------------------------------------

        If only the completion status is available:

        For Example:

            Pulmonary Function Test
            Done
            15/09/2023

        Return
        {{
            "test_name":"Pulmonary Function Test",
            "result":"",
            "unit":"",
            "normal_range":"",
            "status":"Completed",
            "test_date":"2023-09-15"
        }}

        Never store "Done" in result.

        -----------------------------------------
        RULE 3
        -----------------------------------------

        If the report says Pending

        For Example:
            Chest X-Ray
            Pending
            30/10/2023

        Return
        {{
            "test_name":"Chest X-Ray",
            "result":"",
            "unit":"",
            "normal_range":"",
            "status":"Pending",
            "test_date":"2023-10-30"
        }}

        Never store Pending inside result.

        -----------------------------------------
        RULE 4
        -----------------------------------------

        If a qualitative result exists

        For Example:
            COVID PCR
            Positive
            12/05/2024

        Return

        {{
            "test_name":"COVID PCR",
            "result":"Positive",
            "unit":"",
            "normal_range":"",
            "status":"Abnormal",
            "test_date":"2024-05-12"
        }}

        -----------------------------------------
        RULE 5
        -----------------------------------------

        If the report says: Negative, Normal, Reactive, Non-Reactive, Detected, Not Detected. THEN STORE THEM INSIDE RESULT COLUMN

        For Example:
            HIV
            Non-Reactive
            20/01/2024

        Return
        {{
            "test_name":"HIV",
            "result":"Non-Reactive",
            "unit":"",
            "normal_range":"",
            "status":"Normal",
            "test_date":"2024-01-20"
        }}

        -----------------------------------------
        RULE 6
        -----------------------------------------

        Dates ALWAYS and ONLY belong in "test_date"

        Never put dates in "status" or "result".

        -----------------------------------------
        RULE 7
        -----------------------------------------

        Status can ONLY contain one of these values:

        Completed
        Pending
        Unknown

        Never invent any other status.

        -----------------------------------------
        RULE 8
        -----------------------------------------

        If a report contains no actual laboratory value, leave "result" empty.

        For Example:

            Vitamin D
            Done
            15/08/2024

        Return

        {{
            "test_name":"Vitamin D",
            "result":"",
            "unit":"",
            "normal_range":"",
            "status":"Completed",
            "test_date":"2024-08-15"
        }}

        -----------------------------------------
        RULE 9
        -----------------------------------------

        Never swap fields.

        Correct

        {{
            "result":"",
            "status":"Completed",
            "test_date":"2024-09-15"
        }}

        Incorrect

        {{
            "result":"Done",
            "status":"15/09/2024"
        }}

        -----------------------------------------
        FINAL IMPORTANT CHECK POINTS
        -----------------------------------------
        Before generating JSON verify:

        ✓ Dates are only in test_date
        ✓ Name mapping : Done → Completed
        ✓ Pending → Pending
        ✓ Numerical values are only in "result". Keep numerical values exactly as mentioned.
        ✓ Units are only in "unit". Keep units exactly as written.
        ✓ Reference intervals are only in normal_range
        ✓ Every test contains all six fields
        
        Never omit fields.
        Never infer missing values.

        If information is unavailable, use an empty string.

    Note: If a test has no numerical value, do not mention it in the health summary, abnormal findings, recommendations, or possible conditions. Ignore incomplete test results unless they are essential.
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

    {report_text}""").strip()



# -----------------------------
#     ANALYSIS
#     -----------------------------
#     Extract ONLY the information that is explicitly present.

#     If a section is not present, 
#     return an empty list.

#     Never hallucinate.

#     Never infer.
                  
#     Extract the following sections:
                  
#     •Patient Information
#     •Past Medical History
#     •Medications
#     •Allergies
#     •Family History
#     •Social History
#     •Preventive Health
#     •Laboratory Tests