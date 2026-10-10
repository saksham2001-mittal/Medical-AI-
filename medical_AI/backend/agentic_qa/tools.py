from __future__ import annotations
from typing import Dict, Any
from backend.database.models import Patient
from sqlalchemy import func
from langchain_core.tools import tool

from backend.history.history_builder import PatientHistoryService
from backend.agentic_qa.comparison_engine import ComparisonEngine

from backend.agentic_qa.comparison_engine import ComparisonEngine
from backend.agentic_qa.patient_data_retriever import PatientDataRetriever


# ============================================================
# SERVICES
# ============================================================

_history_service = None
_comparison_engine = ComparisonEngine()
_patient_data_retriever = None
_db= None

def initialize_tools(db):
    """
    Initialize services that require a database connection.

    Call this once when creating the application/graph.
    """

    global _history_service
    global _db
    global _patient_data_retriever

    _history_service = PatientHistoryService(db)
    _db = db
    _patient_data_retriever = PatientDataRetriever(db)


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

    # if not patient_history:
    #     return {
    #         "patient_id": patient_id,
    #         "reports": []
    #     }

    # return patient_history
    return (
        patient_history
        or {
            "patient_id": patient_id,
            "reports": [],
        }
    )

# ============================================================
# TOOL 2: GET PATIENT ID BY NAME
# ============================================================

@tool
def get_patient_id_by_name(patient_name: str) -> int:
    """
    Resolve the internal database patient_id using
    the patient's name.
    """

    # if _db is None:
    #     raise RuntimeError(
    #         "Tools have not been initialized. "
    #         "Call initialize_tools(db) first."
    #     )

    # if not patient_name:
    #     raise ValueError("patient_name is required.")

    # patient_name = patient_name.strip()

    # patient = (
    #     _db.query(Patient).filter(
    #         func.lower(Patient.patient_name) == patient_name.lower()).first()
    # )

    # if patient is None:
    #     raise ValueError(
    #         f"No patient found with name: {patient_name}"
    #     )

    # return patient.patient_id
    if _patient_data_retriever is None:
        raise RuntimeError(
            "Tools have not been initialized. Call initialize_tools(db) first."
        )

    return _patient_data_retriever.get_patient_id_by_name(
        patient_name
    )


# ============================================================
# Helper- LIGHTWEIGHT PATIENT DATA
# ============================================================

@tool
def get_patient_reports(patient_id: int) -> Dict[str, Any]:

    """
    Retrieve structured patient/report/test data.

    """

    if _patient_data_retriever is None:
        raise RuntimeError(
            "Tools have not been initialized. "
            "Call initialize_tools(db) first."
        )

    if not patient_id:
        raise ValueError(
            "patient_id is required."
        )

    return _patient_data_retriever.get_patient_reports(
        patient_id
    )


# ============================================================
# TOOL 3: COMPARE TEST RESULTS
# ============================================================

@tool
def compare_test_results(reports: list, test_name: str) -> Dict[str, Any]:
    """
    Compare a specific laboratory test across the patient's available reports.

    """

    if not reports:
        # return {
        #     "test_name": test_name,
        #     "measurements": [],
        #     "changes": [],
        #     "trend": "Insufficient Data",
        # }
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

    if not test_name:
        raise ValueError("test_name is required.")

    return _comparison_engine.compare_test(
        reports=reports, test_name=test_name
    )