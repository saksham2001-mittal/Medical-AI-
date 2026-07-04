from backend.database.connections import SessionLocal
from backend.database.models import (
    Patient,
    Report,
    MedicalTestResult,
    Analysis,
)
from sqlalchemy import func
from backend.schemas.medical_schema import MedicalReport
from backend.schemas.analyse_schema import AnalysisResult
from backend.validator.validation import (validate_patient_name, normalize_patient_name)

def save_medical_report(medical_report: MedicalReport,raw_text: str):
    """
    Save extracted medical report into the database.

    Responsibilities:
        - Find/Create Patient
        - Prevent duplicate reports
        - Store Report
        - Store Test Results

    NOTE:
        Parsing & normalization MUST happen before this function.
    """

    with SessionLocal() as db:

        try:

            patient_info = medical_report.patient_info
            report_info = medical_report.report_info

            # -----------------------------------------------------
            # Validate Patient Name
            # -----------------------------------------------------
            if not validate_patient_name(patient_info.patient_name):
                return {
                    "status": "error",
                    "message": "Invalid patient name extracted."
                }

            clean_name = normalize_patient_name(
                patient_info.patient_name
            )

            # -----------------------------------------------------
            # Find Existing Patient
            # -----------------------------------------------------
            patient = (
                db.query(Patient)
                .filter(
                    func.lower(Patient.patient_name) == clean_name.lower(),

                    Patient.date_of_birth == patient_info.date_of_birth,

                    Patient.phone_no == patient_info.phone_no,

                    func.lower(Patient.gender) == (patient_info.gender or "").lower(),
                )
                .first()
            )

            # -----------------------------------------------------
            # Create Patient
            # -----------------------------------------------------
            if patient is None:

                patient = Patient(
                    patient_name=clean_name,
                    date_of_birth=patient_info.date_of_birth,
                    age=patient_info.age,
                    gender=patient_info.gender,
                    phone_no=patient_info.phone_no,
                )

                db.add(patient)
                db.flush()

            # -----------------------------------------------------
            # Duplicate Report Check
            # -----------------------------------------------------
            existing_report = (
                db.query(Report)
                .filter(
                    Report.patient_id == patient.patient_id,

                    func.lower(Report.report_type)
                    == report_info.report_type.lower(),

                    Report.report_date
                    == report_info.report_date,

                    func.lower(Report.lab_name)
                    == report_info.lab_name.lower(),
                )
                .first()
            )

            if existing_report:

                db.rollback()

                return {
                    "status": "duplicate_report",
                    "message": "Report already exists.",
                    "patient_id": patient.patient_id,
                    "report_id": existing_report.report_id,
                }

            # -----------------------------------------------------
            # Create Report
            # -----------------------------------------------------
            report = Report(
                patient_id=patient.patient_id,
                report_type=report_info.report_type,
                report_date=report_info.report_date,
                lab_name=report_info.lab_name,
                raw_text=raw_text,
            )

            db.add(report)
            db.flush()

            # -----------------------------------------------------
            # Bulk Insert Test Results
            # -----------------------------------------------------
            test_rows = [
                MedicalTestResult(
                    report_id=report.report_id,
                    test_name=test.test_name,
                    value=test.value,
                    unit=test.unit,
                    normal_range=test.normal_range,
                    status=test.status,
                )
                for test in medical_report.test_results
            ]

            if test_rows:
                db.add_all(test_rows)

            db.commit()

            return {
                "status": "success",
                "patient_id": patient.patient_id,
                "report_id": report.report_id,
            }

        except Exception:

            db.rollback()
            raise


def save_analysis(report_id: int, analysis: AnalysisResult):
    """
    Store AI-generated analysis for a report.
    One report can have only one analysis.
    """

    with SessionLocal() as db:

        try:

            existing = (
                db.query(Analysis)
                .filter(
                    Analysis.report_id == report_id
                )
                .first()
            )

            if existing:
                return {
                    "status": "duplicate_analysis",
                    "analysis_id": existing.id,
                }

            db_analysis = Analysis(
                report_id=report_id,

                abnormal_findings=analysis.abnormal_findings,
                possible_conditions=analysis.possible_conditions,
                recommendations=analysis.recommendations,
                lifestyle_advice=analysis.lifestyle_advice,
                follow_up_tests=analysis.follow_up_tests,

                health_summary=analysis.health_summary,
                health_score=analysis.health_score,
                risk_level=analysis.risk_level,
                confidence=analysis.confidence,
            )

            db.add(db_analysis)

            db.commit()

            db.refresh(db_analysis)

            return {
                "status": "success",
                "analysis_id": db_analysis.id,
            }

        except Exception:

            db.rollback()
            raise