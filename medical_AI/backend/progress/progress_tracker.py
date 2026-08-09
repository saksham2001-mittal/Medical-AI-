import json
from datetime import date
from typing import List

from langchain_core.output_parsers import PydanticOutputParser

from backend.core.llm import llm
from backend.progress.progress_prompt import build_progress_prompt
from backend.progress.progress_schema import ProgressSchema


class ProgressTracker:
    """
    Generates longitudinal patient progress using
    all available reports in chronological order.
    """

    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=ProgressSchema)

    def analyze_progress(self, reports: List):
        
        if not reports:
            return ProgressSchema(
                overall_trend="Insufficient Data",
                health_summary="No reports available."
            )

        context = self._prepare_llm_context(reports)

        prompt = build_progress_prompt(
            timeline=context,
            output_schema=self.parser.get_format_instructions(),
        )

        response = llm.invoke(prompt)

        progress = self.parser.parse(response.content)

        return progress

    def _prepare_llm_context(self, reports):

        timeline = []

        for report in reports:

            analysis = report.get("analysis", {})
            tests = []
            for test in report.get("tests", []):
                tests.append(
                    {
                        "test_name": test.get("test_name"),
                        "result": test.get("result"),
                        "normal_range": test.get("normal_range"),
                        "status": test.get("status"),
                        "test_date": test.get("test_date"),
                    }
                )
            timeline.append(
                {
                    "report_date": report.get("report_date"),
                    "report_type": report.get("report_type"),
                    "risk_level": analysis.get("risk_level"),
                    "abnormal_findings": analysis.get("abnormal_findings", []),
                    "possible_conditions": analysis.get("possible_conditions", []),
                    "tests": tests,
                }
            )

        return json.dumps(timeline,indent=2,default=str)