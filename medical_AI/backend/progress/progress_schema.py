from datetime import date
from typing import Literal
from pydantic import BaseModel, Field


TrendType = Literal[
    "Improved",
    "Worsened",
    "Stable",
    "Fluctuating",
    "Insufficient Data"
]


class RiskHistory(BaseModel):
    report_date: date | None = None
    risk_level: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]


class ConditionChange(BaseModel):
    condition: str
    first_seen: date | None = None
    last_seen: date | None = None


class TestTrend(BaseModel):
    test_name: str
    trend: TrendType
    note: str = ""


class ProgressSchema(BaseModel):
    overall_trend: TrendType
    health_summary: str

    risk_history: list[RiskHistory] = Field(
        default_factory=list
    )

    resolved_conditions: list[ConditionChange] = Field(
        default_factory=list
    )

    new_conditions: list[ConditionChange] = Field(
        default_factory=list
    )

    persistent_conditions: list[ConditionChange] = Field(
        default_factory=list
    )

    test_trends: list[TestTrend] = Field(
        default_factory=list
    )

    important_changes: list[str] = Field(
        default_factory=list
    )

    recommended_follow_up: list[str] = Field(
        default_factory=list
    )