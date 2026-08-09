from backend.extraction.medical_schema import (
    MedicalReport,
    PatientInfo,
    ReportInfo,
    TestResult
)

from backend.database.crud import save_medical_report


report = MedicalReport(
    patient_info=PatientInfo(
        patient_name="SaksHAm MiTTal",
        age="25",
        gender="Male",
        date_of_birth="01/01/2005",
        phone_no="9876543299"
    ),
    report_info=ReportInfo(
        report_type="Blood Test",
        report_date="01/08/2026",
        lab_name="Apollo"
    ),
    test_results=[
        TestResult(
            test_name="Hemoglobin",
            value="13.5",
            unit="g/dL",
            normal_range="12-16",
            status="Normal"
        )
    ]
)

result = save_medical_report(
    medical_report=report,
    raw_text="Dummy Report"
)

print(result)