from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from backend.schemas.medical_schema import MedicalReport

load_dotenv()

parser = PydanticOutputParser(
    pydantic_object=MedicalReport
)
llm = ChatOllama(
    model="gemma4:31b-cloud",
    temperature=0
)

prompt = PromptTemplate(
    template="""
        You are an expert medical report extraction system.

        Extract structured information from the medical report.

        {format_instructions}

        Medical Report:
        {report_text}
    """,
    input_variables=["report_text"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    }
)


chain = prompt | llm | parser
def extract_medical_data(report_text: str):

    response = chain.invoke({
        "report_text": report_text
    })
    return response