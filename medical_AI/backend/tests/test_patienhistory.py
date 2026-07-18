from backend.database import SessionLocal
from backend.database.models import Patient
from backend.services.patient_history import PatientHistoryService
import json

db = SessionLocal()

try:
    patient = db.query(Patient).first()

    if patient is None:
        raise Exception("No patients found in database.")

    print(f"Testing Patient: {patient.patient_name}")
    print(f"Patient ID: {patient.patient_id}")

    service = PatientHistoryService(db)

    history = service.build(patient.patient_id)

    print(json.dumps(history, indent=4, default=str))

finally:
    db.close()