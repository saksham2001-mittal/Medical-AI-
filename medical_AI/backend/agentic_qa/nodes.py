from typing import Dict, Any
from backend.agentic_qa.state import PatientQAState
from backend.agentic_qa.tools import (
    get_patient_history,
    get_patient_id_by_name,
    compare_test_results,
)

# =============================================================
# HELPER FUNCTION: TEST IDENTIFICATION
# =============================================================

def _identify_test(question:str, reports:list, llm) -> str:

    """
    Ask the LLM which laboratory test the patient is asking
    about.It only identifies the relevant test name.

    ComparisonEngine performs the actual comparison.
    """

    available_tests = []

    for report in reports:

        for test in report.get("tests", []):

            test_name = test.get("test_name")

            if test_name and test_name not in available_tests:
                available_tests.append(test_name)

    if not available_tests:
        return None

    test_list = "\n".join(f"- {test_name}" for test_name in available_tests)

    identification_prompt = f"""
        You are identifying which laboratory test a patient is asking about.

        Patient question:
        {question}

        Available laboratory tests in the patient's reports:

        {test_list}

        Determine whether the question is asking for a historical
        comparison of one specific laboratory test.

        Rules:

        1. Return ONLY the exact laboratory test name from the list.
        2. Do not create a new test name.
        3. Do not return an explanation.
        4. If the question does not clearly refer to one specific
        laboratory test, return exactly:

        NONE

        Patient question:
        {question}
    """

    response = llm.invoke(identification_prompt)
    identified_test = response.content.strip()
    if identified_test == "NONE":
        return None

    # -----------------------------------------------------
    # Safety check: Only accept a test name that actually exists in the patient's reports.
    # -----------------------------------------------------

    for available_test in available_tests:
        if identified_test.lower() == available_test.lower():
            return available_test
    return None



# =============================================================
# HELPER FUNCTION: TEST GROUP IDENTIFICATION
# =============================================================

def _identify_test_group(question: str, reports: list, llm) -> str:
    """
    Identify whether the patient is asking about a group/panel
    of related laboratory tests.

    Example:

        "What's the status of my Urine Routine test?"

    may correspond to a group containing:

        - RBCs
        - Blood
        - Protein
        - Glucose
        - Nitrite
        etc.

    The LLM only identifies the group.
    It does not perform comparison.
    """

    # ---------------------------------------------------------
    # For now, derive the available report/test information
    # from the patient's actual reports.
    # ---------------------------------------------------------

    available_tests = []

    for report in reports:

        for test in report.get("tests", []):

            test_name = test.get("test_name")

            if test_name and test_name not in available_tests:
                available_tests.append(test_name)

    if not available_tests:
        return None

    test_list = "\n".join(
        f"- {test_name}"
        for test_name in available_tests
    )

    identification_prompt = f"""
        You are identifying whether a patient is asking about a
        laboratory test group or panel.

        Patient question:
        {question}

        Available laboratory tests in the patient's reports:

        {test_list}

        Determine whether the question refers to a GROUP or PANEL
        of related laboratory tests rather than one individual test.

        Examples of group/panel questions include:

        - Urine Routine
        - Complete Blood Count
        - Lipid Profile
        - Liver Function Test
        - Kidney Function Test

        Rules:

        1. Return ONLY the name of the group/panel if the question
        clearly refers to one.

        2. Do not return an individual laboratory test.

        3. Do not create a group that is unrelated to the available
        patient information.

        4. If the question is asking about one specific laboratory test,
        return exactly:

        NONE

        5. If the question is asking about the overall medical report,
        return exactly:

        NONE

        6. Do not return an explanation.

        Patient question:
        {question}
    """

    response = llm.invoke(identification_prompt)

    identified_group = response.content.strip()

    if identified_group.upper() == "NONE":
        return None

    return identified_group


# ============================================================
# NODE 1: LOAD PATIENT HISTORY
# ============================================================

def load_patient_history(state: PatientQAState) -> Dict[str, Any]:
    """
    Load the patient's longitudinal medical history.

    This node uses the get_patient_history tool to retrieve 
    the patient's complete structured history.
    """

    # patient_id = state.get("patient_id")

    # if not patient_id:
    #     raise ValueError("patient_id is required.")
    # print(f"[load_patient_history] Patient ID: {patient_id}")

    patient_name = state.get("patient_name")
    
    if not patient_name:
        raise ValueError("patient name is required.")

    print(f"[load_patient_history] Patient Name: {patient_name}")

    # ---------------------------------------------------------
    # 1. Resolve internal database patient_id
    # ---------------------------------------------------------
    patient_id = get_patient_id_by_name.invoke(
        {
            "patient_name": patient_name
        }
    )

    print(
        f"[load_patient_history] "
        f"Retrieved Patient ID: {patient_id}"
    )

    # ---------------------------------------------------------
    # 2. Load history using internal patient_id
    # ---------------------------------------------------------
    patient_history = get_patient_history.invoke(
        {
            "patient_id": patient_id
        }
    )

    reports = patient_history.get("reports", [])

    return {
        "patient_name": patient_name,
        "patient_id": patient_id,
        "patient_history": patient_history,
        "reports": reports,
    }

# ============================================================
# NODE 2: ANALYZE QUESTION
# ============================================================

def analyze_question(state: PatientQAState, llm) -> Dict[str, Any]:
    """
    Determine what information from the patient's history
    is relevant to the question.
    """

    question = state.get("question", "")
    reports= state.get("reports", [])
    patient_history = state.get("patient_history", {})
    if not question:
        raise ValueError("question is required.")

    print(f"[analyze_question] Question: {question}")

    test_name = _identify_test(question, reports, llm=llm)

    # print(f"[analyze_question] Identified test: {test_name}")
    # return {
    #     "test_name": test_name,
    #     "relevant_data": {
    #         "question": question,
    #         "patient_history": patient_history
    #     }
    # }

    # If no specific test was identified, check if the question refers to a group of related tests.
    test_group = None
    if not test_name:
        test_group = _identify_test_group(question, reports, llm=llm)

    print(
        f"[analyze_question] "
        f"Identified test: {test_name}"
    )

    print(
        f"[analyze_question] "
        f"Identified test group: {test_group}"
    )

    return {
        "test_name": test_name,
        "test_group": test_group,
        "relevant_data": {
            "question": question,
            "patient_history": patient_history,
        },
    }
# ============================================================
# NODE 3: COMPARE TEST RESULTS
# ============================================================

def compare_results(state: PatientQAState,) -> Dict[str, Any]:
    """
    Compare a specific laboratory test across the patient's available reports.
    This node uses the compare_test_results tool to perform the comparison.
    """

    reports = state.get("reports",[])
    test_name = state.get("test_name")

    # --------------------------------------------------------
    # No specific test identified
    # --------------------------------------------------------

    if not test_name:
        print("[compare_results] No test identified.")

        return {
            "comparison_result": {}
        }

    print(f"[compare_results] Comparing test: {test_name}")

    comparison = compare_test_results.invoke(
        {
            "reports": reports,
            "test_name": test_name,
        }
    )

    return {
        "comparison_result": comparison
    }


# ============================================================
# NODE 4: GENERATE FINAL ANSWER
# ============================================================

def generate_answer(state: PatientQAState,llm) -> Dict[str, Any]:
    """
    Generate the final patient-facing answer.

    The LLM receives:
    - the user's question
    - relevant patient information
    - comparison results when available
    """

    question = state.get("question", "")
    patient_history = state.get("patient_history", {})
    comparison_result = state.get("comparison_result",{})
    relevant_data = state.get("relevant_data",{})
    
    if not question:
        raise ValueError("question is required.")
    print(f"[generate_answer] Generating answer for: {question}")

    # --------------------------------------------------------
    # Build evidence
    # --------------------------------------------------------
    
    evidence = {
        "patient_history": patient_history,
        "relevant_data": relevant_data,
        "comparison": comparison_result,
    }
    prompt = f"""
        You are a medical information assistant.

        Your task is to answer the user's question using ONLY the
        patient information provided below.

        The patient information may contain:

        - Patient details
        - Laboratory reports
        - Laboratory test values
        - Reference ranges
        - Longitudinal trends
        - Previous report comparisons
        - Clinical findings
        - Other relevant medical information

        ==================================================
        EVIDENCE AND SAFETY RULES
        ==================================================

            1. Use only information present in the provided patient
            information.

            2. DO NOT INVENT THE FOLLOWING:

            - laboratory values
            - dates
            - reference ranges
            - diagnoses
            - medications
            - treatments
            - symptoms
            - medical history

            3. Do not assume that a missing test or value exists.

            4. If the available information is insufficient to answer
            the question, clearly state that the available data is
            insufficient and explain what information is missing.

            5. Distinguish between:

            - an observed laboratory value
            - a change in that value
            - an interpretation of that change
            - a diagnosis or disease progression

            6. Do not diagnose the patient unless the provided information
            explicitly contains that diagnosis.

            7. Do not provide treatment decisions or medication instructions.
            If appropriate, recommend discussing the finding with a
            qualified healthcare professional.


        ==================================================
        UNDERSTANDING THE USER'S QUESTION
        ==================================================

        First determine what the user is actually asking.

        The question may involve:

            - A single test
            - A group of related tests
            - Comparison with previous reports
            - Improvement or worsening
            - A general health condition
            - A specific report
            - Changes between two dates
            - Whether sufficient information exists to answer the question

            Select only the patient information relevant to the question.

            Do not include unrelated tests simply because they are available.


        ==================================================
        COMPARISON RULES
        ==================================================

        When the question involves change over time or comparison with previous reports:

            1. Use the available reports in chronological order.

            2. Include the actual dates and values.

            3. Compare consecutive available measurements.

            4. Calculate numerical changes when the units are compatible.

            5. Determine the trend based on the observed values:

            - Improved:
            The values moved consistently in a favorable direction.

            - Worsened:
            The values moved consistently in an unfavorable direction.

            - Fluctuating:
            The values moved in different directions across the
            available measurements.

            - Stable:
            The values remained substantially unchanged.

            - Insufficient Data:
            There is not enough information to determine a trend.

            6. Do not describe a fluctuating test as simply improved or
            worsened.

            7. When a comparison result is already provided, use that
            comparison as the primary evidence for the numerical changes.


        ==================================================
        RESPONSE REQUIREMENTS
        ==================================================
        For questions involving comparison of laboratory results:

            1. Start with a direct answer to the user's question.

            2. Identify the relevant laboratory tests.

            3. When comparing laboratory results, show:

            - test name
            - date
            - value
            - unit
            - change from the previous available report

            4. Explain the direction of change in simple language:

            - Improved
            - Worsened
            - Fluctuating
            - Stable
            - Insufficient Data

            5. Do not only say "improved" or "worsened".
            Explain what changed using the actual values.

            6. If the report contains a reference range, mention whether
            the latest value is within or outside that report's
            reference range.

            7. Do not invent a reference range when one is not available.

            8. Clearly distinguish between:

            - change in a laboratory value
            - interpretation of that change
            - diagnosis or disease progression

            9. Use simple language that a patient can understand.

            10. Avoid unnecessary medical terminology. If a medical term
                is necessary, briefly explain it.

            11. Do not overwhelm the user with unrelated tests.
                Only include tests relevant to the question.

            12. Only include information relevant to the question.

            13. If the available information is insufficient, explicitly
            state what information is missing.

            14. End with a short "Bottom line" statement answering the
            user's original question.


        ==================================================
        PATIENT EVIDENCE
        ==================================================

        {evidence}

        ==================================================
        USER QUESTION
        ==================================================

        {question}

        Provide a Concise, Evidence-Grounded Answer.
    """

    response = llm.invoke(prompt)

    return {
        "answer": response.content
    }