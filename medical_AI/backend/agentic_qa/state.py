from typing import Any, Dict, List, Optional, TypedDict


class PatientQAState(TypedDict, total=False):

    # ---------------- INPUT ----------------
    patient_name: str
    question: str

    # ---------------- PATIENT DATA ----------------
    patient_id: int
    patient_history: Dict[str, Any]
    reports: List[Dict[str, Any]]

    # ---------------- QUESTION ANALYSIS ----------------
    question_type: Optional[str]
    test_name: Optional[str]
    test_group: Optional[str]
    # name of the test group, if applicable
    group_tests: List[str]

    needs_patient_data: bool
    needs_comparison: bool
    needs_medical_context: bool

    # # ---------------- RETRIEVED / RELEVANT INFORMATION ----------------
    # relevant_data: Dict[str, Any]

    # ---------------- Medical knowledge retrieved through RAG ----------------
    medical_context: str

    # ---------------- COMPARISON ----------------
    comparison_result: Dict[str, Any]
    # Used when multiple tests are compared
    comparison_results: Dict[str, Any]
    
    # ---------------- FINAL Response ----------------
    evidence: Dict[str, Any]
    answer: str