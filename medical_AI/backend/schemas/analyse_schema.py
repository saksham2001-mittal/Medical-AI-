from pydantic import BaseModel
from typing import List


class AbnormalFinding(BaseModel):
    test_name: str
    observation: str


class AnalysisResult(BaseModel):

    overall_health_summary: str

    abnormal_findings: List[AbnormalFinding]

    possible_health_concerns: List[str]

    health_score: int

    risk_level: str