from backend.agentic_qa.graph import build_patient_qa_graph
from backend.agentic_qa.tools import (initialize_tools)
from backend.core.llm import llm

class AgenticPatientQAService:

    def __init__(self, db):

        # ----------------------------------------------------
        # Initialize agentic QA tools with the database
        # ----------------------------------------------------

        initialize_tools(db)
        self.graph = build_patient_qa_graph(llm=llm)

    # def answer_question(self, patient_id: int, question: str) -> str:
    def answer_question(self, patient_name: str, question: str) -> str:
        """
        Run the patient QA LangGraph workflow.
        """

        # if not patient_id:
        #     raise ValueError("patient_id is required.")
        if not patient_name:
            raise ValueError("patient_name is required.")

        if not question:
            raise ValueError("question is required.")

        # ----------------------------------------------------
        # Initial state
        # ----------------------------------------------------

        initial_state = {
            # "patient_id": patient_id,
            "patient_name": patient_name,
            "question": question,
        }

        # ----------------------------------------------------
        # Run LangGraph
        # ----------------------------------------------------

        final_state = self.graph.invoke(initial_state)

        # ----------------------------------------------------
        # Return final answer
        # ----------------------------------------------------

        return final_state.get(
            "answer", "Unable to generate an answer."
        )