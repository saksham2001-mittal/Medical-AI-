from backend.agentic_qa.graph import patient_qa_graph
from backend.agentic_qa.tools import initialize_tools
from backend.database.connections import SessionLocal

db = SessionLocal()

try:

    initialize_tools(db)
    # questions = ["What is my haemoglobin?",
    #         "Has my haemoglobin changed?",
    #         "Has my haemoglobin improved?",
    #         "Is my haemoglobin normal?",
    #         "What does haemoglobin mean?",]

    # for q in questions:
    #     answer = patient_qa_graph.invoke(
    #             {
    #                 "patient_name": "Sanjay Mittal",
    #                 "question": q,
    #             }
    #         )

    #     print("\nFINAL ANSWER:")
    #     print(answer["answer"])
    answer = patient_qa_graph.invoke(
        {
        "patient_name": "Sanjay Mittal",
         "question":"Has my haemoglobin improved?", }
                )
    
    print("\nFINAL ANSWER:")
    print(answer["answer"])

finally:
    db.close()


# service = AgenticPatientQAService(db)
# questions = ["whats the status of my Hemoglobin. Is it improved from last time?",
#             "Whats the status of overall blood report as compared to previous reports?",
#             "What's the status of Urine Routine test? Is it improving or not?",
#             "What's the status of my Vitamin D levels?",
#             "Is My complete blood count report normal or not?",
#             "Is my Cholesterol level good or bad?",]

# for q in questions:
#     answer = service.answer_question(
#         patient_name="Sanjay Mittal",
#         question=q
#     )
#     print(answer)