from backend.schemas.medical_schema import MedicalReport

def get_report_category(report: MedicalReport) -> str:
    """
    Classify the extracted report.

    Returns:
        - lab
        - summary
        - prescription
        - radiology
        - unknown
    """

    report_type = (report.report_info.report_type or "").lower()

    if any(
        keyword in report_type
        for keyword in [
            "lab",
            "laboratory",
            "blood",
            "pathology",
            "medical tests",
            "test report",
        ]
    ):
        return "lab"

    if any(
        keyword in report_type
        for keyword in [
            "summary",
            "patient summary",
            "clinical summary",
            "consultation",
        ]
    ):
        return "summary"

    if any(
        keyword in report_type
        for keyword in [
            "prescription",
            "medication",
        ]
    ):
        return "prescription"

    if any(
        keyword in report_type
        for keyword in [
            "radiology",
            "xray",
            "x-ray",
            "ct",
            "mri",
            "ultrasound",
        ]
    ):
        return "radiology"

    # fallback

    if report.test_results:
        has_values = any(test.result for test in report.test_results)

        if has_values:
            return "lab"

        return "summary"

    return "unknown"