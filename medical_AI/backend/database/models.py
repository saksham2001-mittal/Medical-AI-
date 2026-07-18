from sqlalchemy import *

from sqlalchemy.orm import relationship
from backend.database.connections import Base
from sqlalchemy.sql import func

class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String(150), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20))
    phone_no = Column(String(25))
    created_at = Column(TIMESTAMP, server_default=func.now())

    reports = relationship(
        "Report",
        back_populates="patient"
    )


class Report(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.patient_id")
    )

    report_type = Column(String(100))
    report_date = Column(Date)
    lab_name = Column(String(150))
    raw_text = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    patient = relationship("Patient", back_populates="reports")

    test_results = relationship(
        "MedicalTestResult",
        back_populates="report"
    )

    analysis = relationship(
        "Analysis",
        back_populates="report",
        uselist=False,
        cascade="all, delete-orphan"
    )

class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(
        Integer,
        ForeignKey("reports.report_id"),
        nullable=False,
        unique=True
    )

    abnormal_findings = Column(JSON)
    possible_conditions = Column(JSON)
    recommendations = Column(JSON)
    lifestyle_advice = Column(JSON)
    follow_up_tests = Column(JSON)
    health_summary = Column(Text)
    risk_level = Column(String(20))

    
    report = relationship(
        "Report",
        back_populates="analysis"
    )

class MedicalTestResult(Base):
    __tablename__ = "test_results"

    test_id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer,ForeignKey("reports.report_id") )

    test_name = Column(String(150))
    result = Column(String(100))
    unit = Column(String(30))
    normal_range = Column(String(50))
    status = Column(String(20))
    # Date when the test was performed
    test_date = Column(Date, nullable=True)
    
    report = relationship(
        "Report", 
        back_populates="test_results")