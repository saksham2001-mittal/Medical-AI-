from pydantic import BaseModel, Field
from typing import List
from datetime import date

class PatientInfo(BaseModel):
    patient_name: str = ""
    date_of_birth: date | None = None
    age: int | None = None
    gender: str | None = None
    phone_no: str | None = None


class ReportInfo(BaseModel):
    report_type: str = ""
    report_date: date | None = None
    lab_name: str = ""


class TestResult(BaseModel):
    test_name: str = ""
    value: str = ""
    unit: str = ""
    normal_range: str = ""
    status: str = ""


class MedicalReport(BaseModel):
    patient_info: PatientInfo
    report_info: ReportInfo
    # test_results: List[TestResult] = []
    test_results: list[TestResult] = Field(default_factory=list)