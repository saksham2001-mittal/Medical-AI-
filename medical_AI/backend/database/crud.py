from datetime import timedelta

from backend.database.connections import SessionLocal
from backend.database.models import (Patient, Report, MedicalTestResult)
from backend.database.utils import (parse_age, parse_date)
from backend.schemas.medical_schema import MedicalReport

def save_medical_report(medical_report: MedicalReport, raw_text: str):

    db = SessionLocal()
    try:

        # -------------------------
        # PATIENT Information
        # -------------------------
        

        patient_age = parse_age(medical_report.patient_info.age)
        created_at = parse_date(medical_report.report_info.report_date)


        existing_patient = (db.query(Patient).filter(
                Patient.patient_name.ilike(medical_report.patient_info.patient_name),
                Patient.age == patient_age,
                Patient.date_of_birth == parse_date(medical_report.patient_info.date_of_birth),
                Patient.gender.ilike(medical_report.patient_info.gender),
                Patient.created_at >= created_at - timedelta(days=365)
            )
            .first()
        )
        # print("DOB:", parse_date(medical_report.patient_info.date_of_birth))
        # print("AGE:", patient_age)
        # print("PHONE:", medical_report.patient_info.phone_no)
        if existing_patient:
            patient = existing_patient

        else:
            patient = Patient(
                patient_name=medical_report.patient_info.patient_name,
                age=patient_age,
                gender=medical_report.patient_info.gender,
                date_of_birth=parse_date(medical_report.patient_info.date_of_birth) or "Not Found",
                phone_no=medical_report.patient_info.phone_no or "Not Found",
                created_at=created_at

            )
            print(medical_report.model_dump())
            db.add(patient)
            db.commit()
            db.refresh(patient)

        # -------------------------
        # REPORT
        # -------------------------

        report = Report(
            patient_id=patient.patient_id,
            report_type=medical_report.report_info.report_type,
            report_date=parse_date(medical_report.report_info.report_date),
            lab_name=medical_report.report_info.lab_name,
            raw_text=raw_text,
            created_at=created_at

        )
        print(medical_report.report_info)
        db.add(report)
        db.commit()
        db.refresh(report)

        # -------------------------
        # TEST RESULTS
        # -------------------------

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