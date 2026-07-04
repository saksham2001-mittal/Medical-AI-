from langchain_ollama import ChatOllama

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from backend.schemas.medical_schema import MedicalReport
from backend.schemas.analyse_schema import AnalysisResult

parser = PydanticOutputParser(pydantic_object=AnalysisResult)
llm = ChatOllama(model="gemma4:31b-cloud", temperature=0)

prompt = PromptTemplate(
    template="""
        You are an experienced physician specializing in laboratory report interpretation.

        IMPORTANT RULES

        - You are NOT diagnosing diseases.
        - Only analyze the information present.
        - Never invent laboratory values.
        - Never invent medical history.
        - Never assume symptoms.
        - If every result is normal, clearly mention that.
        - Recommendations should be educational and should encourage consultation with healthcare professionals when appropriate.
        - Return ONLY valid JSON.
        - Do not include markdown.
        - Follow the output schema exactly.

        Tasks

        1. Identify abnormal laboratory findings.
        2. Explain what each abnormal finding may indicate.
        3. List possible conditions supported ONLY by the report.
        4. Generate a concise health summary.
        5. Give practical lifestyle advice.
        6. Suggest follow-up laboratory tests if needed.
        7. Assign a health score (0-100).
        8. Assign a risk level:
        - Low
        - Medium
        - High
        9. Estimate confidence (0-1).

        {format_instructions}

        Medical Report

        {medical_report}
        """,
    input_variables=["medical_report"],
    partial_variables={ "format_instructions": parser.get_format_instructions() }
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
        lines.append(
            f"{test.test_name}: "
            f"{test.value} {test.unit} | "
            f"Range: {test.normal_range} | "
            f"Status: {test.status}"
        )

    return "\n".join(lines)

def analyze_medical_report(
    medical_report: MedicalReport
) -> AnalysisResult:

    formatted_report = format_report(medical_report)

    return chain.invoke(
        {
            "medical_report": formatted_report
        }
    )