from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session
from backend.database import crud
from datetime import datetime, time
from backend.services.history_extractor import HistoryExtractor

class PatientHistoryService:
    """
    Service responsible for building a complete patient history from all reports available in the database.

    Responsibilities
    ----------------
    - Build patient profile
    - Build report timeline
    - Build report objects
    - Aggregate longitudinal patient history
    - Compute patient statistics

    """

    def __init__(self, db: Session):
        self.db = db
        self.history_extractor = HistoryExtractor()

    def build(self, patient_id: int):

        patient_record = crud.get_complete_patient_data(
            self.db,
            patient_id
        )

        if patient_record is None:
            raise ValueError(
                f"Patient with ID {patient_id} not found."
            )

        reports = [
            report.raw_text
            for report in patient_record.reports
            if report.raw_text
        ]

        patient_history = self.history_extractor.extract(reports)

        return {
            "patient": self._build_patient_info(patient_record),
            "timeline": self._build_timeline(patient_record),
            "reports": self._build_reports(patient_record),
            "history": patient_history,
            "statistics": self._build_statistics(patient_record),
        }
    # ==========================================================
    # Public API
    # ==========================================================

    # def build(self, patient_id: int) -> dict[str, Any]:
    #     """
    #     Build the complete patient history.

    #     Parameters
    #     ----------
    #     patient_id : int

    #     Returns
    #     -------
    #     dict:  Complete patient history object.
    #     """

    #     patient_record = crud.get_complete_patient_data(self.db, patient_id)

    #     if patient_record is None:
    #         raise ValueError(f"Patient with ID {patient_id} not found.")

    #     history = {
    #         "patient": self._build_patient_profile(patient_record),
    #         "timeline": self._build_timeline(patient_record),
    #         "reports": self._build_reports(patient_record),
    #         "history": self._aggregate_history(patient_record),
    #         "statistics": self._build_statistics(patient_record)
    #     }

    #     return history

    # ==========================================================
    # Patient Profile
    # ==========================================================

    def _build_patient_info(self, patient) -> dict[str, Any]:
        """
        Build basic patient profile.
        """

        return {
            "patient_id": patient.patient_id,
            "patient_name": patient.patient_name,
            "date_of_birth": patient.date_of_birth,
            "age": patient.age,
            "gender": patient.gender,
            "phone_no": patient.phone_no,
            "created_at": patient.created_at,
        }

    # ==========================================================
    # Timeline
    # ==========================================================

    def _build_timeline(self, patient) -> list[dict[str, Any]]:
        """
        Create chronological report timeline.

        This timeline is later helps in creating:
        - Report comparison
        - Trend analysis
        - Longitudinal health tracking
        """

        timeline = []

        # reports = sorted(
        #     patient.reports,
        #     key=lambda report: (report.report_date if report.report_date else report.created_at)
        # )
        reports = sorted(
            patient.reports,
            key=lambda report: (
                datetime.combine(report.report_date, time.min) if report.report_date else report.created_at
            )
        )


        for report in reports:

            timeline.append({
                "report_id": report.report_id,
                "report_date": report.report_date,
                "report_type": report.report_type,
                "lab_name": report.lab_name,
                "created_at": report.created_at
            })

        return timeline
    
    # ==========================================================
    # Reports
    # ==========================================================

    def _build_reports(self, patient_record ) -> list[dict[str, Any]]:
        """
        Build all reports belonging to a patient.

        Every report contains
        - Report metadata
        - Laboratory test results
        - AI analysis
        """

        reports = []

        sorted_reports = sorted(
            patient_record.reports,
            key=lambda report: (
                datetime.combine(report.report_date, time.min) if report.report_date else report.created_at
            )
        )
        for report in sorted_reports:
            report_data = {
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
                    }
                    for test in report.test_results
                ],

                "analysis": self._build_analysis(report.analysis)
            }

            reports.append(report_data)
        return reports


    # ==========================================================
    # Analysis
    # ==========================================================

    def _build_analysis(self, analysis) -> dict[str, Any] | None:
        """
        Convert Analysis ORM object into a JSON serializable dictionary.
        Analysis represents AI-generated interpretation of a laboratory report.
        """

        if analysis is None:
            return None
        
        return {

            "abnormal_findings": analysis.abnormal_findings or [],
            "possible_conditions":analysis.possible_conditions or [],
            "recommendations":analysis.recommendations or [],
            "lifestyle_advice":analysis.lifestyle_advice or [],
            "follow_up_tests":analysis.follow_up_tests or [],
            "health_summary":analysis.health_summary,
            "risk_level":analysis.risk_level

        }
    
    # ==========================================================
    # History Aggregation
    # ==========================================================

    # def _aggregate_history(self, patient_record) -> dict[str, Any]:
    #     """
    #     Aggregates patient history by combining AI analysis from every report.

    #     """

    #     history = {

    #         "past_medical_history": [],
    #         "possible_conditions": [],
    #         "recommendations": [],
    #         "lifestyle_advice": [],
    #         "follow_up_tests": [],
    #         "risk_levels": [],
    #         "health_summaries": []

    #     }

    #     for report in patient_record.reports:

    #         analysis = report.analysis
    #         if analysis is None:
    #             continue

    #         history["possible_conditions"].extend(analysis.possible_conditions or [])
    #         history["recommendations"].extend(analysis.recommendations or [])
    #         history["lifestyle_advice"].extend(analysis.lifestyle_advice or [])
    #         history["follow_up_tests"].extend(analysis.follow_up_tests or [])

    #         if analysis.risk_level:
    #             history["risk_levels"].append(analysis.risk_level)

    #         if analysis.health_summary:
    #             history["health_summaries"].append(analysis.health_summary)

    #     # Remove duplicate values

    #     history["possible_conditions"] = self._unique(history["possible_conditions"])
    #     history["recommendations"] = self._unique(history["recommendations"])
    #     history["lifestyle_advice"] = self._unique(history["lifestyle_advice"])
    #     history["follow_up_tests"] = self._unique(history["follow_up_tests"])
    #     history["risk_levels"] = self._unique(history["risk_levels"])
    #     history["past_medical_history"] = list(history["possible_conditions"])

    #     return history

    # # ==========================================================
    # # Helper
    # # ==========================================================

    # def _unique(self, values: list[Any]) -> list[Any]:
    #     """
    #     Remove duplicates while preserving order.
    #     """

    #     unique_values = []
    #     seen = set()

    #     for value in values:

    #         if value is None:
    #             continue

    #         if isinstance(value, str):
    #             key = value.strip().lower()
    #         else:
    #             key = str(value)

    #         if key not in seen:
    #             seen.add(key)
    #             unique_values.append(value)

    #     return unique_values
    
    # ==========================================================
    # Statistics
    # ==========================================================

    def _build_statistics(self, patient_record) -> dict[str, Any]:
        """
        Compute overall patient statistics.
        These statistics are useful for dashboards, trend analysis and future AI services.
        """

        reports = patient_record.reports
        total_reports = len(reports)
        total_tests = sum( len(report.test_results) for report in reports)
        latest_report = None
        if reports:
            latest_report = max(
                reports,
                key=lambda report: (datetime.combine(report.report_date, time.min) if report.report_date else report.created_at
                )
            )
        # -----------------------------
        # Risk Levels
        # -----------------------------

        risk_history = []
        for report in reports:
            if report.analysis is None:
                continue
            if report.analysis.risk_level is None:
                continue
            risk_history.append({
                "report_id": report.report_id,
                "report_date": report.report_date,
                "risk_level": report.analysis.risk_level

            })

        latest_risk = ( risk_history[-1]["risk_level"] if risk_history else None )

        return {
            "total_reports": total_reports,
            "total_tests": total_tests,
            "latest_report_date": latest_report.report_date if latest_report else None,
            "latest_risk_level":latest_risk,
            "risk_history": risk_history
        }

    # ==========================================================
    # Convenience APIs
    # ==========================================================

    def get_latest_report(self,patient_id: int):
        """
        Return latest report for a patient.
        """

        patient_record = crud.get_complete_patient_data(self.db,patient_id)
        if not patient_record:
            return None

        if not patient_record.reports:
            return None

        # return max(
        #     patient_record.reports, key=lambda report: (report.report_date if report.report_date else report.created_at)
        # )
        return max(
        patient_record.reports,
        key=lambda report: (
            datetime.combine(report.report_date, time.min) if report.report_date else report.created_at
            )
        )


    def report_count(self,patient_id: int) -> int:
        """
        Return number of reports uploaded by a patient.
        """

        patient_record = crud.get_complete_patient_data(self.db,patient_id)

        if patient_record is None:
            return 0

        return len(patient_record.reports)
    