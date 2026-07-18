import json

from backend.prompts.patient_history_prompt import build_patient_history_prompt
from backend.llm.llm_model import invoke


class HistoryExtractor:
    """
    Extracts a structured longitudinal patient history
    from one or more normalized report.raw_text values.
    """

    def extract(self, reports: list[str]) -> dict:
        """
        Parameters
        ----------
        reports : list[str]
            List of normalized report.raw_text belonging to the same patient.

        Returns
        -------
        dict
            Structured patient history returned by the LLM.
        """

        if not reports:
            return {}

        merged_report = self._merge_reports(reports)

        prompt = build_patient_history_prompt(merged_report)

        response = invoke(prompt)

        return self._parse_response(response)

    def _merge_reports(self, reports: list[str]) -> str:
        """
        Merge multiple reports into a single document.
        """

        sections = []

        report_number = 1

        for report in reports:

            report = report.strip()

            if not report:
                continue

            sections.append(
                f"\n{'=' * 25} REPORT {report_number} {'=' * 25}\n"
            )

            sections.append(report)

            report_number += 1

        return "\n".join(sections)

    def _parse_response(self, response) -> dict:
        """
        Convert the LLM response into a Python dictionary.
        """

        if hasattr(response, "content"):
            response = response.content

        response = response.strip()

        # Remove markdown formatting if present
        response = response.replace("```json", "")
        response = response.replace("```", "").strip()

        try:
            return json.loads(response)

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON returned by LLM.\n\nResponse:\n{response}"
            ) from e