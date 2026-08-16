from langgraph.graph import StateGraph, START, END

from backend.agentic_qa.state import PatientQAState
from backend.agentic_qa.nodes import (
    load_patient_history, analyze_question, generate_answer, compare_results
)

# ============================================================
# ==================== ROUTING LOGIC =========================
# ============================================================

def route_after_analysis(state: PatientQAState) -> str:
    """
    Decide whether the question requires a test comparison.

    If a specific laboratory test was identified:
        -> compare_results

    If no specific test was identified:
        -> generate_answer directly
    """

    test_name = state.get("test_name")

    if test_name:
        print(
            f"[route_after_analysis] "
            f"Specific test identified: {test_name}"
        )

        return "compare_results"

    print(
        "[route_after_analysis] "
        "No specific test identified. "
        "Skipping comparison."
    )

    return "generate_answer"

#============================================================
#===================== BUILD GRAPH ==========================
#============================================================

def build_patient_qa_graph(llm):
    """
    Build and compile the Patient QA LangGraph.

    Flow:
        START
          ↓
    load_patient_history
          ↓
      analyze_question
          ↓
      compare_results
          ↓
      generate_answer
          ↓
         END
    """

    workflow = StateGraph(PatientQAState)

    # --------------------------------------------------------
    # Add nodes
    # --------------------------------------------------------

    workflow.add_node("load_patient_history",load_patient_history)

    workflow.add_node("analyze_question", lambda state: analyze_question(state, llm=llm))

    workflow.add_node("compare_results", compare_results)

    workflow.add_node("generate_answer", lambda state: generate_answer(state, llm=llm))

    # --------------------------------------------------------
    # Define edges
    # --------------------------------------------------------

    workflow.add_edge(START, "load_patient_history")

    workflow.add_edge("load_patient_history", "analyze_question")

    # workflow.add_edge("analyze_question", "compare_results")

    # Conditional routing based on whether a specific test was identified
    workflow.add_conditional_edges("analyze_question",
        route_after_analysis,
        {
            "compare_results": "compare_results",
            "generate_answer": "generate_answer",
        },
    )

    # Final Comparison
    workflow.add_edge("compare_results", "generate_answer")

    # Final Answer
    workflow.add_edge("generate_answer", END)

    # --------------------------------------------------------
    # Compile graph
    # --------------------------------------------------------

    return workflow.compile()


