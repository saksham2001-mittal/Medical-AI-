from typing import Dict, Any
from backend.database.models import Patient
from sqlalchemy import func
from langchain_core.tools import tool

from backend.history.history_builder import PatientHistoryService
from backend.agentic_qa.comparison_engine import ComparisonEngine


# ============================================================
# SERVICES
# ============================================================

_history_service = None
_comparison_engine = ComparisonEngine()
_db= None

def initialize_tools(db):
    """
    Initialize services that require a database connection.

    Call this once when creating the application/graph.
    """

    global _history_service
    global _db

    _history_service = PatientHistoryService(db)
    _db = db


# ============================================================
# TOOL 1: GET PATIENT HISTORY
# ============================================================

@tool
def get_patient_history(patient_id: int) -> Dict[str, Any]:
    """
    Retrieve the complete longitudinal medical history for a patient.
    """

    if _history_service is None:
        raise RuntimeError(
            "Tools have not been initialized. "
            "Call initialize_tools(db) first."
        )

    if not patient_id:
        raise ValueError("patient_id is required.")

    patient_history = _history_service.build(patient_id)

    if not patient_history:
        return {
            "patient_id": patient_id,
            "reports": []
        }

    return patient_history

@tool
def get_patient_id_by_name(patient_name: str) -> int:
    """
    Resolve the internal database patient_id using
    the patient's name.
    """

    if _db is None:
        raise RuntimeError(
            "Tools have not been initialized. "
            "Call initialize_tools(db) first."
        )

    if not patient_name:
        raise ValueError("patient_name is required.")

    patient_name = patient_name.strip()

    patient = (
        _db.query(Patient).filter(
            func.lower(Patient.patient_name) == patient_name.lower()).first()
    )

    if patient is None:
        raise ValueError(
            f"No patient found with name: {patient_name}"
        )

    return patient.patient_id

# ============================================================
# TOOL 2: COMPARE TEST RESULTS
# ============================================================

@tool
def compare_test_results(reports: list, test_name: str) -> Dict[str, Any]:
    """
    Compare a specific laboratory test across
    the patient's available reports.

    The actual numerical comparison is handled by
    ComparisonEngine.
    """

    if not reports:
        return {
            "test_name": test_name,
            "measurements": [],
            "changes": [],
            "trend": "Insufficient Data",
        }

    if not test_name:
        raise ValueError("test_name is required.")

    return _comparison_engine.compare_test(
        reports=reports,
        test_name=test_name)