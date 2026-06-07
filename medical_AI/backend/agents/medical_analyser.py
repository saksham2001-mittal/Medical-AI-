from langchain_ollama import ChatOllama

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from backend.schemas.medical_schema import MedicalReport
from backend.schemas.analyse_schema import AnalysisResult

parser = PydanticOutputParser(pydantic_object=AnalysisResult)
llm = ChatOllama(model="gemma4:31b-cloud", temperature=0)

prompt = PromptTemplate(
    template="""
        You are an expert medical analyst.

        Analyze the extracted medical report.

        Your task:

        1. Identify abnormal findings.
        2. Identify possible health concerns.
        3. Generate an overall health summary.
        4. Assign a health score between 0 and 100.
        5. Assign a risk level:
        - Low
        - Medium
        - High

        {format_instructions}

        Medical Report:

        {medical_report}
    """,
    input_variables=["medical_report"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)


chain = prompt | llm | parser


def analyze_medical_report(
    medical_report: MedicalReport
) -> AnalysisResult:

    return chain.invoke(
        {
            "medical_report":
            medical_report.model_dump_json(
                indent=2
            )
        }
    )