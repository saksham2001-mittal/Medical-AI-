from backend.analysis.medical_analyzer import (analyze_medical_report)
from backend.extraction.medical_schema import (
    MedicalReport,
    PatientInfo,
    ReportInfo,
    TestResult
)

from backend.preprocessing.report_classifier import get_report_category


report = MedicalReport(
    patient_info=PatientInfo(
        patient_name="Saksham Mittal",
        age=24,
        gender="Male"
    ),

    
    report_info= ReportInfo(
        report_type="Blood Test",
        report_date="2025-03-09",
        lab_name="Healthians"
    ),

    test_results=[
        TestResult(
            test_name="Triglycerides",
            result="220",
            unit="mg/dL",
            normal_range="<150",
            status="Completed",
            test_date= "2024-10-30"
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

def run_analysis(report):
    category = get_report_category(report)

    if category != "lab":
        return None

    if not any(test.result.strip() for test in report.test_results):
        return None

    return analyze_medical_report(report)

result= run_analysis(report)
print(result.model_dump())