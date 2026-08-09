# from typing import List
# from pydantic import BaseModel, Field


# class ConditionInsight(BaseModel):
#     """
#     Summary of a clinically relevant condition.
#     """
#     name: str
#     status: str = ""
#     note: str = ""

# class TestInsight(BaseModel):
#     """
#     Summary of an important laboratory test.
#     """
#     test_name: str
#     status: str = ""
#     note: str = ""

# class RecommendationInsight(BaseModel):
#     """
#     Frequently recurring recommendation.
#     """
#     recommendation: str
#     frequency: int = 1

# class ClinicalInsights(BaseModel):
#     """
#     High-level clinical intelligence generated from all available reports.
#     """

#     active_conditions: List[ConditionInsight] = Field(default_factory=list)

#     high_risk_conditions: List[ConditionInsight] = Field(default_factory=list)

#     improving_conditions: List[ConditionInsight] = Field(default_factory=list)

#     pending_tests: List[TestInsight] = Field(default_factory=list)

#     frequently_abnormal_tests: List[TestInsight] = Field(default_factory=list)

#     recurring_recommendations: List[RecommendationInsight] = Field(default_factory=list)

#     care_gaps: List[str] = Field(default_factory=list)


from pydantic import BaseModel
from typing import Literal


class ConditionInsight(BaseModel):
    name: str
    status: Literal[
        "Persistent",
        "New",
        "Improving",
        "Worsening"
    ]
    note: str = ""


class TestInsight(BaseModel):
    test_name: str
    abnormal_report_count: int
    total_report_count: int
    note: str = ""


class ClinicalInsightSchema(BaseModel):
    active_conditions: list[ConditionInsight]
    high_risk_conditions: list[ConditionInsight]
    improving_conditions: list[ConditionInsight]
    frequently_abnormal_tests: list[TestInsight]