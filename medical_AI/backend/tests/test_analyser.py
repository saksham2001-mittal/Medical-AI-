from backend.agents.medical_analyser import (analyze_medical_report)
from backend.schemas.medical_schema import (
    MedicalReport,
    PatientInfo,
    ReportInfo,
    TestResult
)

report = MedicalReport(
    patient_info=PatientInfo(
        patient_name="Saksham Mittal",
        age=24,
        gender="Male"
    ),

    report_info=ReportInfo(
        report_type="Blood Test",
        report_date="09/03/2025",
        lab_name="Healthians"
    ),

    test_results=[
        TestResult(
            test_name="Triglycerides",
            value="220",
            unit="mg/dL",
            normal_range="<150",
            status="High"
        ),

        TestResult(
            test_name="HDL",
            value="35",
            unit="mg/dL",
            normal_range=">40",
            status="Low"
        )
    ]
)

result = analyze_medical_report(
    report
)

print(result.model_dump())