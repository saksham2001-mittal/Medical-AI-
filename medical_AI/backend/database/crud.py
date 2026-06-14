from datetime import timedelta
from backend.database.utils import (
    validate_patient_name,
    normalize_patient_name
)
from backend.database.connections import SessionLocal
from backend.database.models import (Patient, Report, MedicalTestResult)
from backend.database.utils import (parse_age, parse_date)
from backend.schemas.medical_schema import MedicalReport

def save_medical_report(medical_report: MedicalReport, raw_text: str):

    db = SessionLocal()
    try:
        # ===============  CLEAN + VALIDATE PATIENT DATA =============
        raw_name = medical_report.patient_info.patient_name
        if not validate_patient_name(raw_name):
            return { "status": "error", "message": "Invalid patient name extracted" }
        
        clean_name = normalize_patient_name(raw_name)
        patient_age = parse_age(medical_report.patient_info.age)
        patient_dob = parse_date(medical_report.patient_info.date_of_birth)
        report_date = parse_date(medical_report.report_info.report_date)
        phone_no = medical_report.patient_info.phone_no
        
        # ================= FIND EXISTING PATIENT =================
        existing_patient = existing_patient = (
                    db.query(Patient)
                    .filter(
                        Patient.patient_name.ilike(clean_name),
                        Patient.date_of_birth == patient_dob,
                        Patient.phone_no == phone_no,
                        Patient.gender.ilike(medical_report.patient_info.gender)
                    ).first() )
        
        # ================= CREATE PATIENT ==================
        if existing_patient:
            patient = existing_patient
        else:
            patient = Patient(
                patient_name=clean_name,
                age=patient_age,
                gender=medical_report.patient_info.gender,
                date_of_birth=patient_dob,
                phone_no=phone_no,
                # created_at=report_date
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)

        # ================ CHECK DUPLICATE REPORT ==================
        existing_report = (db.query(Report)
                           .filter(Report.patient_id == patient.patient_id,
                                   Report.report_type.ilike(medical_report.report_info.report_type),
                                   Report.report_date == report_date,
                                   Report.lab_name.ilike(medical_report.report_info.lab_name))
                           .first())
        
        if existing_report:
            return {
                "status": "duplicate_report",
                "message": "Report already exists",
                "patient_id": patient.patient_id,
                "report_id": existing_report.report_id
            }
        
        # ===================== CREATE REPORT ======================
        report = Report(
            patient_id=patient.patient_id,
            report_type=medical_report.report_info.report_type,
            report_date=report_date,
            lab_name=medical_report.report_info.lab_name,
            raw_text=raw_text,
            # created_at=report_date
        )
        db.add(report)
        db.commit()
        db.refresh(report)


        # =================== STORE TEST RESULTS ======================
        for test in medical_report.test_results:
            test_row = MedicalTestResult(
                report_id=report.report_id,
                test_name=test.test_name,
                value=test.value,
                unit=test.unit,
                normal_range=test.normal_range,
                status=test.status
            )
            db.add(test_row)
        db.commit()

        return {
            "status": "success",
            "patient_id": patient.patient_id,
            "report_id": report.report_id
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()