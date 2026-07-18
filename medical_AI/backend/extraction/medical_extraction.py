from __future__ import annotations

import json
import logging

# from dotenv import load_dotenv

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from backend.llm.llm_model import invoke
from pydantic import ValidationError
from sqlalchemy import exc
from backend.services.report_classifier import get_report_category
from backend.validator.parsing import normalize_extracted_json
from backend.schemas.medical_schema import MedicalReport
from backend.prompts.medical_prompt import build_medical_prompt
from backend.services.report_normaliser import normalize_raw_ocr_text

# load_dotenv()
logger = logging.getLogger(__name__)

parser = PydanticOutputParser(pydantic_object=MedicalReport)

# # -------------------------------------------------------------------
# # Prompt
# # -------------------------------------------------------------------

# prompt = PromptTemplate(
#     template = build_medical_prompt(),
#     input_variables=["report_text"],
#     partial_variables={
#         "format_instructions": parser.get_format_instructions()
#     },
# )

# chain = prompt | llm


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _extract_json(content: str) -> dict:
    """
    Extract JSON object returned by Gemma.
    Raises ValueError if valid JSON cannot be found.
    """

    content = content.strip()

    if content.startswith("```"):
        lines = content.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object found in LLM response.")

    json_text = content[start:end + 1]

    return json.loads(json_text)


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------

def extract_medical_data(report_text: str) -> MedicalReport:

    # ---------------------------------------------------------------
    # Step 1 Normalize OCR
    # ---------------------------------------------------------------

    normalized_text = normalize_raw_ocr_text(report_text)
    logger.debug("OCR normalization completed.")

    # ---------------------------------------------------------------
    # Step 2 Prompt + LLM
    # ---------------------------------------------------------------

    prompt = build_medical_prompt(
            report_text=normalized_text,
            output_schema=MedicalReport.model_json_schema())
    response = invoke(prompt)

    logger.debug("LLM response received.")

    # ---------------------------------------------------------------
    # Step 3 Extract JSON
    # ---------------------------------------------------------------

    try:
        extracted_json = _extract_json(response.content)
    except Exception as exc:
        logger.exception("Failed to extract JSON from model output.")
        raise ValueError(
            "Model returned invalid JSON."
        ) from exc

    # ---------------------------------------------------------------
    # Step 4
    # Validate using Pydantic
    # ---------------------------------------------------------------

    try:
        normalized_json = normalize_extracted_json(extracted_json)
        report = MedicalReport.model_validate(normalized_json)
        category = get_report_category(report)
        logger.info(f"Detected report category : {category}")

    except ValidationError as exc:
        logger.exception("Medical report validation failed.")
        raise ValueError(f"Pydantic validation failed:\n{exc}") from exc
    logger.info("Medical report extracted successfully.")

    print("=" * 80)
    print("MEDICAL REPORT AFTER PARSING")
    print("=" * 80)

    for test in report.test_results:
        print(test.model_dump())
    return report