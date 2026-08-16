from typing import Any, Dict, List, TypedDict, Optional


class PatientQAState(TypedDict, total=False):
    # ---------------------------------------------------------
    # User input
    # ---------------------------------------------------------
    patient_name: str
    patient_id: int
    question: str

    # ---------------------------------------------------------
    # Patient data
    # ---------------------------------------------------------
    patient_history: Dict[str, Any]
    reports: List[Dict[str, Any]]

    # ---------------------------------------------------------
    # Relevant data for comparison
    # ---------------------------------------------------------
    relevant_data: Dict[str, Any]
    test_name: Optional[str]

    test_group: Optional[str]
    # ---------------------------------------------------------
    # Comparison result
    # ---------------------------------------------------------
    comparison_result: Dict[str, Any]

    # ---------------------------------------------------------
    # Final response
    # ---------------------------------------------------------
    answer: str