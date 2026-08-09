# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser

# from backend.schemas.medical_schema import MedicalReport
# from backend.schemas.analyse_schema import AnalysisResult
# from backend.llm.llm_model import llm 

# parser = PydanticOutputParser(pydantic_object=AnalysisResult)

# prompt = PromptTemplate(
#     template="""
#         You are an experienced physician specializing in laboratory report interpretation.

#         IMPORTANT RULES

#         - You are NOT diagnosing diseases.
#         - Only analyze the information present.
#         - Never invent laboratory values.
#         - Never invent medical history.
#         - Never assume symptoms.
#         - If every result is normal, clearly mention that.
#         - Recommendations should be educational and should encourage consultation with healthcare professionals when appropriate.
#         - Return ONLY valid JSON.
#         - Do not include markdown.
#         - Follow the output schema exactly.

#         Tasks

#         1. Identify abnormal laboratory findings.
#         2. Explain what each abnormal finding may indicate.
#         3. List possible conditions supported ONLY by the report.
#         4. Generate a concise health summary.
#         5. Give practical lifestyle advice.
#         6. Suggest follow-up laboratory tests if needed.
#         7. Assign a risk level:
#         - Low
#         - Medium
#         - High

#         {format_instructions}

#         Medical Report

#         {medical_report}
#         """,
#     input_variables=["medical_report"],
#     partial_variables={ "format_instructions": parser.get_format_instructions() }
# )

# chain = prompt | llm | parser

# def format_report(report: MedicalReport) -> str:

#     patient = report.patient_info
#     report_info = report.report_info
#     lines = []

#     lines.append("PATIENT INFORMATION")
#     lines.append(f"Name: {patient.patient_name}")
#     lines.append(f"Age: {patient.age}")
#     lines.append(f"Gender: {patient.gender}")
#     lines.append("")

#     lines.append("REPORT INFORMATION")
#     lines.append(f"Type: {report_info.report_type}")
#     lines.append(f"Date: {report_info.report_date}")
#     lines.append(f"Lab: {report_info.lab_name}")
#     lines.append("")

#     lines.append("LAB RESULTS")

#     for test in report.test_results:
#         lines.append(
#             f"{test.test_name}: "
#             f"{test.result} {test.unit} | "
#             f"Range: {test.normal_range} | "
#             f"Status: {test.status} | "
#             f"test_date:{test.test_date}"
#         )

#     return "\n".join(lines)

# def analyze_medical_report(
#     medical_report: MedicalReport
# ) -> AnalysisResult:

#     formatted_report = format_report(medical_report)

#     return chain.invoke(
#         {
#             "medical_report": formatted_report
#         }
#     )

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from backend.extraction.medical_schema import MedicalReport
from backend.analysis.analysis_schema import AnalysisResult
from backend.core.llm import llm

parser = PydanticOutputParser(pydantic_object=AnalysisResult)

prompt = PromptTemplate(
    template="""
    You are an experienced physician specializing in laboratory report interpretation.

    IMPORTANT RULES

    - You are NOT diagnosing diseases.
    - Only analyze the information present.
    - Never invent laboratory values.
    - Never invent medical history.
    - Never assume symptoms.
    - Return ONLY valid JSON.
    - Do not include markdown.
    - Follow the output schema exactly.

    Laboratory Test Interpretation Rules

    - Only interpret tests that contain an actual numerical or qualitative result.
    - Ignore tests whose status is "Completed" or "Pending" but have no result.
    - Never treat "Completed" as a medical finding.
    - Never treat "Pending" as an abnormality.
    - If all available tests are completed or pending without actual values, clearly state that no laboratory interpretation can be made.

    Tasks

    1. Identify abnormal laboratory findings.
    2. Explain what each abnormal finding may indicate.
    3. List possible conditions supported ONLY by the report.
    4. Generate a concise health summary.
    5. Give practical lifestyle advice.
    6. Suggest follow-up laboratory tests if needed.
    7. Assign a risk level:
    - Low
    - Medium
    - High

    {format_instructions}

    Medical Report

    {medical_report}
    """,
    input_variables=["medical_report"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
        },
)

chain = prompt | llm | parser


def format_report(report: MedicalReport) -> str:

    patient = report.patient_info
    report_info = report.report_info

    lines = []

    lines.append("PATIENT INFORMATION")
    lines.append(f"Name: {patient.patient_name}")
    lines.append(f"Age: {patient.age}")
    lines.append(f"Gender: {patient.gender}")
    lines.append("")

    lines.append("REPORT INFORMATION")
    lines.append(f"Type: {report_info.report_type}")
    lines.append(f"Date: {report_info.report_date}")
    lines.append(f"Lab: {report_info.lab_name}")
    lines.append("")

    lines.append("LAB RESULTS")

    for test in report.test_results:

        line = [f"Test: {test.test_name}"]

        if test.result:
            line.append(f"Result: {test.result}")

        if test.unit:
            line.append(f"Unit: {test.unit}")

        if test.normal_range:
            line.append(f"Range: {test.normal_range}")

        if test.status:
            line.append(f"Status: {test.status}")

        if test.test_date:
            line.append(f"Date: {test.test_date}")

        lines.append(" | ".join(line))

    return "\n".join(lines)


def analyze_medical_report(medical_report: MedicalReport) -> AnalysisResult:

    formatted_report = format_report(medical_report)

    analysis = chain.invoke(
        {
            "medical_report": formatted_report
        }
    )

    print("=" * 80)
    print("LLM OUTPUT")
    print("=" * 80)
    print(analysis.model_dump_json(indent=4))

    return analysis