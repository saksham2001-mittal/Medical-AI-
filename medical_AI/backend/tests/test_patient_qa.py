# from backend.database import SessionLocal
# from backend.database.models import Patient
# from backend.qa.patient_qa import PatientQAService
# from backend.core.llm import llm


# def main():

#     db = SessionLocal()

#     try:

#         patient = (
#             db.query(Patient)
#             .order_by(Patient.patient_id.desc())
#             .first()
#         )

#         if patient is None:
#             print("No patient found.")
#             return

#         question = "Whats the status of overall report as compared with my previous reports?"

#         service = PatientQAService(
#             db=db,
#             llm=llm,
#         )

#         answer = service.answer_question(
#             patient_id=patient.patient_id,
#             question=question,
#         )

#         print("=" * 70)
#         print("PATIENT QUESTION")
#         print("=" * 70)

#         print(question)

#         print("\n" + "=" * 70)
#         print("ANSWER")
#         print("=" * 70)

#         print(answer)

#     finally:
#         db.close()


# if __name__ == "__main__":
#     main()


from backend.agentic_qa.service import AgenticPatientQAService
from backend.database import SessionLocal
db = SessionLocal()

service = AgenticPatientQAService(db)
questions = ["whats the status of my Hemoglobin. Is it improved from last time?",
            "Whats the status of overall blood report as compared to previous reports?",
            "What's the status of Urine Routine test? Is it improving or not?",
            "What's the status of my Vitamin D levels?",
            "Is My complete blood count report normal or not?",
            "Is my Cholesterol level good or bad?",]

for q in questions:
    answer = service.answer_question(
        patient_name="Sanjay Mittal",
        question=q
    )
    print(answer)