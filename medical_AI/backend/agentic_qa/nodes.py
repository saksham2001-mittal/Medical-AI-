from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional
from backend.agentic_qa.state import PatientQAState
from backend.agentic_qa.tools import (compare_test_results, get_patient_id_by_name, get_patient_reports)

# ============================================================
# TEST HELPERS
# ============================================================
def _get_available_tests(reports: list) -> list[str]:
    available_tests: list[str] = []
    seen: set[str] = set()

    for report in reports:
        for test in report.get("tests", []):
            name = test.get("test_name")
            if not name:
                continue

            key = str(name).casefold().strip()
            if key not in seen:
                seen.add(key)
                available_tests.append(name)
    return available_tests


def _clean_json_response(content: str) -> dict:
    text = (content or "").strip()

    # Remove Markdown code fences.
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", " ", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try extracting the first JSON object.
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
    return {}


def _match_available_test(candidate: Any, available_tests: list[str],) -> Optional[str]:
    if not candidate:
        return None

    candidate = str(candidate).strip().casefold()

    for test_name in available_tests:
        if candidate == test_name.casefold().strip():
            return test_name

    return None

def _select_group_tests(candidates: Any, available_tests: list[str]) -> list[str]:
    if not isinstance(candidates, list):
        return []

    selected: list[str] = []

    for candidate in candidates:
        matched = _match_available_test(candidate, available_tests)

        if matched and matched not in selected:
            selected.append(matched)

    return selected

def _fallback_test_match(question: str, available_tests: list[str]) -> Optional[str]:
    """
    Conservative fallback if the LLM fails to identify a valid test name.
    """
    normalized_question = re.sub(r"[^a-z0-9]+", " ", question.casefold()).strip()

    # Longer test names first.
    for test_name in sorted(available_tests, key=len, reverse=True):
        normalized_test = re.sub(r"[^a-z0-9]+", " ", test_name.casefold()).strip()

        if normalized_test and normalized_test in normalized_question:
            return test_name

    return None

# ============================================================
# NODE 1: LOAD PATIENT DATA
# ============================================================

def load_patient_data(state: PatientQAState) -> Dict[str, Any]:
    patient_name = state.get("patient_name")

    if not patient_name:
        raise ValueError("patient name is required.")

    print(f"[load_patient_data] Patient Name: {patient_name}")

    patient_id = get_patient_id_by_name.invoke({"patient_name": patient_name})
    patient_data = get_patient_reports.invoke({"patient_id": patient_id})
    reports = patient_data.get("reports", [])

    print(f"[load_patient_data] Patient ID: {patient_id}")
    print(f"[load_patient_data] Reports loaded: {len(reports)}")

    # print("\n[load_patient_data] Report data:")

    # response= json.dumps(
    #         reports,
    #         indent=2,
    #         default=str
    #     )
    # output_file = r"C:\Users\mitta\OneDrive\Desktop\AI_project\medical_AI\answer_output.txt"
    # with open(output_file, "w", encoding="utf-8") as f:
    #     f.write(response)
    # print(f"\nSaved answer to: {output_file}")

    return {
        "patient_id": patient_id,
        "patient_data": patient_data,
        "reports": reports,
    }

# ============================================================
# NODE 2: QUESTION ANALYSIS
# ============================================================

def analyze_question(state: PatientQAState, llm) -> Dict[str, Any]:
    question = state.get("question", "").strip()
    reports = state.get("reports", [])

    if not question:
        raise ValueError("question is required.")

    available_tests = _get_available_tests(reports)
    test_list = "\n".join(f"- {name}" for name in available_tests) or "NONE"

    prompt = f"""
        You are a Medical-Report Analysis Assistant. 
        
        Your job is to ONLY analyze the patient's question and determine what information they are asking for.

        Do not compare laboratory values.
        Do not diagnose.
        Do not determine medical significance.
        Do not provide medical advice.

        PATIENT QUESTION:
        {question}

        AVAILABLE TESTS IN THE PATIENT'S REPORTS:
        {test_list}

        Return ONLY valid JSON:

        {{
            "question_type": "specific_test | test_group | overall",

            "test_name": "exact available test name or null",

            "test_group": "group or panel name or null",

            "group_tests": ["exact available test names"],

            "needs_patient_data": true,

            "needs_comparison": true,

            "needs_medical_context": true
        }}

        RULES:

        1. test_name MUST exactly match one of the available tests or be null.
        2. group_tests may contain ONLY names from the available test list.
        3. Use "specific_test" when the question concerns one particular laboratory test.
        4. Use "test_group" when the question concerns a named group or panel.
        5. Use "overall" for broad questions involving the patient's reports generally.
        6. needs_comparison should be true when the patient asks about:
        - change
        - comparison
        - previous reports
        - history
        - trend
        - progression
        - increase/decrease over time
        7. needs_patient_data should be false only when the question does not require the patient's own report data.
        8. needs_medical_context should be true when the patient asks:
        - what a test means
        - why it matters
        - what a change may signify
        - what the result generally means
        - when professional consultation may be appropriate
        9. Never diagnose the patient.
        10. Never determine medical severity.
    """

    response = llm.invoke(prompt)
    parsed = _clean_json_response(response.content)

    question_type = parsed.get("question_type")
    if question_type not in {"specific_test", "test_group", "overall"}:
        question_type = "overall"

    test_name = _match_available_test(parsed.get("test_name"), available_tests)
    group_tests = _select_group_tests(parsed.get("group_tests"), available_tests)

    # --------------------------------------------------------
    # Fallback for specific test
    # --------------------------------------------------------
    if question_type == "specific_test" and not test_name:
        test_name = _fallback_test_match(question, available_tests)
        if not test_name:
            question_type = "overall"

    # --------------------------------------------------------
    # Group fallback
    # --------------------------------------------------------
    if question_type == "test_group" and not group_tests:
        question_type = "overall"

    needs_patient_data = bool(parsed.get("needs_patient_data", True))
    needs_comparison = bool(parsed.get("needs_comparison", False))
    needs_medical_context = bool(parsed.get("needs_medical_context", False))

    # Current QA entry point always represents a patient-specific question.
    needs_patient_data = True

    print(f"[analyze_question] Type: {question_type}")
    print(f"[analyze_question] Test: {test_name}")
    print(f"[analyze_question] Group: {parsed.get('test_group')}")
    print(f"[analyze_question] Group tests: {group_tests}")
    print(f"[analyze_question] Needs comparison: {needs_comparison}")
    print(f"[analyze_question] Needs medical context: {needs_medical_context}")

    return {
        "question_type": question_type,
        "test_name": test_name,
        "test_group": parsed.get("test_group") if question_type == "test_group" else None,
        "group_tests": group_tests,
        "needs_patient_data": needs_patient_data,
        "needs_comparison": needs_comparison,
        "needs_medical_context": needs_medical_context,
    }

# ============================================================
# NODE 3: COMPARISON
# ============================================================

def compare_results(state: PatientQAState) -> Dict[str, Any]:
    reports = state.get("reports", [])
    question_type = state.get("question_type")
    test_name = state.get("test_name")
    group_tests = state.get("group_tests", [])

    if not state.get("needs_comparison", False):
        return {
            "comparison_result": {},
            "comparison_results": {},
        }

    # --------------------------------------------------------
    # Specific test
    # --------------------------------------------------------
    if question_type == "specific_test" and test_name:
        comparison = compare_test_results.invoke(
            {
                "reports": reports,
                "test_name": test_name,
            }
        )
        print("\n[compare_results] Comparison result:")
        print(json.dumps(comparison,indent=2,default=str))
        return {
            "comparison_result": comparison,
            "comparison_results": {test_name: comparison},
        }

    # --------------------------------------------------------
    # Test group
    # --------------------------------------------------------
    if question_type == "test_group":
        comparison_results = {}

        for current_test in group_tests:
            comparison_results[current_test] = compare_test_results.invoke(
                {
                    "reports": reports,
                    "test_name": current_test,
                }
            )

        return {
            "comparison_result": {},
            "comparison_results": comparison_results,
        }

    # --------------------------------------------------------
    # Overall
    # --------------------------------------------------------
    available_tests = _get_available_tests(reports)
    comparison_results = {}

    for current_test in available_tests:
        comparison_results[current_test] = compare_test_results.invoke(
            {
                "reports": reports,
                "test_name": current_test,
            }
        )

    return {
        "comparison_result": {},
        "comparison_results": comparison_results,
    }

# ============================================================
# EVIDENCE
# ============================================================

# def _build_evidence(state: PatientQAState) -> Dict[str, Any]:
#     question_type = state.get("question_type")
#     test_name = state.get("test_name")
#     test_group = state.get("test_group")
#     group_tests = state.get("group_tests", [])
#     comparison_result = state.get("comparison_result", {})
#     comparison_results = state.get("comparison_results", {})
#     medical_context = state.get("medical_context", "")

#     # --------------------------------------------------------
#     # Specific test
#     # --------------------------------------------------------
#     if question_type == "specific_test":
#         return {
#             "evidence_type": "specific_test",
#             "question": state.get("question", ""),
#             "test_name": test_name,

#             # Complete longitudinal history
#             "measurements": comparison_result.get("measurements", []),

#             # Consecutive changes between reports
#             "changes": comparison_result.get( "changes", []),

#             # Deterministic summary
#             "overall_trend": comparison_result.get("overall_trend"),
#             "latest_change": comparison_result.get("latest_change"),
#             "latest_value": comparison_result.get("latest_value"),
#             "previous_value": comparison_result.get("previous_value"),
#             "reference_range": comparison_result.get("reference_range"),
#             "latest_status": comparison_result.get("latest_status"),
#              "medical_context": medical_context,
#         }

#     # --------------------------------------------------------
#     # Test group
#     # --------------------------------------------------------
#     if question_type == "test_group":
#         return {
#             "evidence_type": "test_group",
#             "question": state.get("question", ""),
#             "test_group": test_group,
#             "tests": {
#                 name: comparison_results.get(name)
#                 for name in group_tests if comparison_results.get(name)
#             },
#             "medical_context": medical_context,
#         }

#     # --------------------------------------------------------
#     # Overall
#     # --------------------------------------------------------
#     return {
#         "evidence_type": "overall_report",
#         "question": state.get("question", ""),
#         "tests": comparison_results,
#         "medical_context": medical_context,
#     }

def _build_evidence(state: PatientQAState) -> Dict[str, Any]:
    question_type = state.get("question_type")
    test_name = state.get("test_name")
    test_group = state.get("test_group")
    group_tests = state.get("group_tests", [])

    reports = state.get("reports", [])
    comparison_result = state.get("comparison_result", {})
    comparison_results = state.get("comparison_results", {})
    medical_context = state.get("medical_context", "")

    # ---------------------------------------------------------
    # Specific test questions
    # ---------------------------------------------------------
    if question_type == "specific_test":

        latest_result = None

        if test_name:
            target_test = test_name.strip().lower()

            # Reports are already sorted chronologically
            for report in reports:
                report_date = report.get("report_date")

                for test in report.get("tests", []):
                    current_test = (test.get("test_name") or "").strip().lower()

                    if current_test == target_test:
                        latest_result = {
                            "date": report_date,
                            "value": test.get("result"),
                            "unit": test.get("unit"),
                            "reference_range": test.get("normal_range"),
                            "status": test.get("status"),
                        }

        return {
            "evidence_type": "specific_test",
            "question": state.get("question", ""),
            "test_name": test_name,

            # Patient data directly from already-loaded reports
            "latest_result": latest_result,

            # Comparison evidence, available when comparison was performed
            "measurements": comparison_result.get("measurements", []),
            "changes": comparison_result.get("changes", []),
            "overall_trend": comparison_result.get("overall_trend"),
            "latest_change": comparison_result.get("latest_change"),
            "latest_value": comparison_result.get("latest_value"),
            "previous_value": comparison_result.get("previous_value"),
            "reference_range": comparison_result.get("reference_range"),
            "latest_status": comparison_result.get("latest_status"),

            "medical_context": medical_context,
        }

    # ---------------------------------------------------------
    # Test group questions
    # ---------------------------------------------------------
    if question_type == "test_group":
        return {
            "evidence_type": "test_group",
            "question": state.get("question", ""),
            "test_group": test_group,
            "tests": {
                name: comparison_results.get(name)
                for name in group_tests
                if comparison_results.get(name)
            },
            "medical_context": medical_context,
        }

    # ---------------------------------------------------------
    # Overall report questions
    # ---------------------------------------------------------
    return {
        "evidence_type": "overall_report",
        "question": state.get("question", ""),
        "tests": comparison_results,
        "medical_context": medical_context,
    }

# ============================================================
# NODE 4: FINAL ANSWER
# ============================================================

def generate_answer(state: PatientQAState, llm) -> Dict[str, Any]:
    question = state.get("question", "").strip()

    if not question:
        raise ValueError("question is required.")

    evidence = _build_evidence(state)

    prompt = f"""
        You are a User Support Assistant for a medical report analysis system.
         
        Your task is to answer the patient's question using ONLY the structured evidence provided below.

        PATIENT QUESTION:
        {question}

        STRUCTURED EVIDENCE:
        {json.dumps(evidence, indent=2, default=str)}

        RULES:

            1. Answer the patient's actual question directly.
            2. Patient-specific facts must come ONLY from the supplied evidence.
            3. Preserve values, units, dates and reported reference ranges exactly.
            4. For comparison questions, use the supplied pairwise changes and overall trend.
            5. If the trend is fluctuating, describe it as fluctuating.
            6. Do not assume:
            - increase = improvement
            - decrease = worsening
            7. A laboratory reference range describes the laboratory's reported range.
            Being outside that range does not by itself establish a diagnosis.
            8. Do not invent:
            - diagnoses
            - causes
            - symptoms
            - treatments
            - medications
            - medical risks
            9. If medical_context is empty, do not invent medical explanations from general knowledge.
            10. Keep the answer natural, concise and easy for a patient to understand.
            11. Do not mention:
                - databases
                - agents
                - prompts
                - tools
                - internal processing
            12. Do not dump unrelated historical information.
            13. If multiple reports are available, use the longitudinal evidence provided
                rather than looking only at the latest two reports.
            14. If the question asks about changes "over my reports", "over time",
                "over the years", "across my reports", or similar longitudinal wording,
                summarize the complete available measurement history in chronological order.
            15. For a longitudinal question:
                - mention each available measurement date and value when there are only a small number of reports (for example, 2-5 reports).
                - describe each supplied pairwise change in chronological order.
                - then summarize the overall trend.
                - do not reduce the answer to only the latest and previous report.
            16. Do not calculate new changes yourself. Use only the supplied "changes" values and directions.
            17. Keep the chronological history concise. Do not provide unnecessary details
                unrelated to the patient's question.

        Return ONLY the final answer.
    """

    response = llm.invoke(prompt)
    answer = response.content.strip()

    return {
        "evidence": evidence,
        "answer": answer,
    }