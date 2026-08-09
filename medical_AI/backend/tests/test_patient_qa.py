from backend.database import SessionLocal
from backend.database.models import Patient
from backend.qa.patient_qa import PatientQAService
from backend.core.llm import llm


def main():

    db = SessionLocal()

    try:

        patient = (
            db.query(Patient)
            .order_by(Patient.patient_id.desc())
            .first()
        )

        if patient is None:
            print("No patient found.")
            return

        question = "Whats the status of overall report as compared with my previous reports?"

        service = PatientQAService(
            db=db,
            llm=llm,
        )

        answer = service.answer_question(
            patient_id=patient.patient_id,
            question=question,
        )

        print("=" * 70)
        print("PATIENT QUESTION")
        print("=" * 70)

        print(question)

        print("\n" + "=" * 70)
        print("ANSWER")
        print("=" * 70)

        print(answer)

    finally:
        db.close()


if __name__ == "__main__":
    main()