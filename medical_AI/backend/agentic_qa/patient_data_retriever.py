from __future__ import annotations

from datetime import datetime, time
from typing import Any, Dict, List

from sqlalchemy.orm import Session, selectinload

from backend.database.models import Patient, Report


class PatientDataRetriever:
    """
    Lightweight patient-data retrieval service used by Agentic QA.

    It retrieves structured patient/report/test data from the database.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_patient_id_by_name(self, patient_name: str) -> int:

        if not patient_name or not patient_name.strip():
            raise ValueError("patient_name is required.")

        patient = (
            self.db.query(Patient).filter(Patient.patient_name.ilike(patient_name.strip())).first()
            )

        if patient is None:
            raise ValueError(f"No patient found with name: {patient_name}")

        return patient.patient_id

    def get_patient_reports(self,patient_id: int) -> Dict[str, Any]:

        patient = (
            self.db.query(Patient)
            .options(selectinload(Patient.reports).selectinload(Report.test_results))
            .filter(Patient.patient_id == patient_id).first()
        )

        if patient is None:
            raise ValueError(f"Patient with ID {patient_id} not found.")

        reports = sorted(
            patient.reports,
            key=lambda report: (
                datetime.combine(report.report_date,time.min) if report.report_date else report.created_at),
        )

        report_data: List[Dict[str, Any]] = []

        for report in reports:

            report_data.append(
                {
                    "report_id": report.report_id,
                    "report_type": report.report_type,
                    "report_date": report.report_date,
                    "lab_name": report.lab_name,
                    "created_at": report.created_at,

                    "tests": [
                        {
                            "test_id": test.test_id,
                            "test_name": test.test_name,
                            "result": test.result,
                            "unit": test.unit,
                            "normal_range": test.normal_range,
                            "status": test.status,
                            "test_date": test.test_date,
                        }
                        for test in report.test_results
                    ],
                }
            )

        return {
            "patient": {
                "patient_id": patient.patient_id,
                "patient_name": patient.patient_name,
                "date_of_birth": patient.date_of_birth,
                "age": patient.age,
                "gender": patient.gender,
            },
            "reports": report_data,
        }