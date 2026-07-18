from pydantic import BaseModel, Field
from typing import List


class AbnormalFinding(BaseModel):
    test_name: str
    observation: str

class AnalysisResult(BaseModel):
    abnormal_findings: List[str] = Field(
        default_factory=list,
        description="Abnormal laboratory findings."
    )

    possible_conditions: List[str] = Field(
        default_factory=list,
        description="Possible medical conditions suggested by the abnormal findings. Do not diagnose."
    )

    health_summary: str = Field(
        description="Simple overall health summary."
    )

    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommended next medical actions."
    )

    lifestyle_advice: List[str] = Field(
        default_factory=list,
        description="Lifestyle improvements."
    )

    follow_up_tests: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up laboratory tests."
    )
    
    risk_level: str = Field(
        description="Low, Medium or High."
    )