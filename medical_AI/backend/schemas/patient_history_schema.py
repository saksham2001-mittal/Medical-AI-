from pydantic import BaseModel
from typing import Optional


class MedicalHistoryEvent(BaseModel):
    event_date: Optional[str] = None
    event_type: Optional[str] = None
    description: str
    source_report_id: Optional[int] = None