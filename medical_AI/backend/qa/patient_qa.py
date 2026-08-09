# from backend.history.history_builder import PatientHistoryService
# from backend.qa.comparison_engine import ComparisonEngine


# class PatientQAService:

#     def __init__(self, db, llm):
#         self.db = db
#         self.llm = llm

#         self.history_service = PatientHistoryService(db)
#         self.comparison_engine = ComparisonEngine()

#     def answer_question(self, patient_id: int, question: str):

#         # ---------------------------------------------------------
#         # 1. Get patient's longitudinal history
#         # ---------------------------------------------------------

#         patient_history = self.history_service.build(patient_id)

#         # ---------------------------------------------------------
#         # 2. Extract reports from patient history
#         # ---------------------------------------------------------

#         reports = patient_history.get("reports", [])

#         # ---------------------------------------------------------
#         # 3. Identify whether this is a comparison question
#         # ---------------------------------------------------------

#         test_name = self._identify_test(question)

#         # ---------------------------------------------------------
#         # 4. If a test is identified, use ComparisonEngine
#         # ---------------------------------------------------------

#         if test_name:

#             comparison = self.comparison_engine.compare_test(reports=reports, test_name=test_name)

#             # Use comparison result as the evidence
#             # given to the LLM.
#             evidence = { "comparison": comparison }

#         else:

#             # -----------------------------------------------------
#             # 5. For non-comparison questions, use patient history
#             # -----------------------------------------------------

#             evidence = patient_history

#         # ---------------------------------------------------------
#         # 6. Build the existing prompt
#         # ---------------------------------------------------------

#         prompt = self._build_prompt(
#             question=question,
#             patient_history=evidence,
#         )

#         # ---------------------------------------------------------
#         # 7. Ask the LLM to generate the final answer
#         # ---------------------------------------------------------

#         response = self.llm.invoke(prompt)

#         return response.content

#     # =============================================================
#     # TEST IDENTIFICATION
#     # =============================================================

#     def _identify_test(self, question: str):

#         question_lower = question.lower()

#         # Keep this simple for M1.
#         # We are not doing aliases or complex mappings here.

#         test_keywords = {
#             "hba1c": "HbA1c",
#             "hemoglobin": "Haemoglobin (HB)",
#             "haemoglobin": "Haemoglobin (HB)",
#             "vitamin d": "Vitamin D Total-25 Hydroxy",
#             "vitamin b12": "Vitamin B12",
#             "hdl": "HDL Cholesterol Direct",
#             "cholesterol": "Cholesterol Total",
#             "triglycerides": "Triglycerides, Serum",
#             "creatinine": "Serum Creatinine",
#             "gfr": "GFR, ESTIMATED",
#             "egfr": "GFR, ESTIMATED",
#             "fasting glucose": "Glucose, Fasting",
#             "fasting blood sugar": "Fasting Blood Sugar",
#             "blood sugar": "Glucose, Fasting",
#             "iron": "Serum Iron",
#             "ferritin": "Ferritin",
#             "tsh": "Thyroid Stimulating Hormone (TSH)-Ultrasensitive",
#         }

#         for keyword, test_name in test_keywords.items():

#             if keyword in question_lower:
#                 return test_name

#         return None

#     # =============================================================
#     # EXISTING PROMPT
#     # =============================================================

#     def _build_prompt(self, question, patient_history):

#         return f"""
#         You are a medical information assistant.

#         Answer the user's question using ONLY the patient information provided below.

#         Do not invent:
#         - diagnoses
#         - laboratory values
#         - dates
#         - medications
#         - treatments
#         - clinical history

#         If the available patient information does not
#         contain enough evidence to answer the question,
#         clearly say that the available data is insufficient.

#         When comparing laboratory values:

#         1. Use the actual dates.
#         2. Use the actual values.
#         3. Mention whether the value improved,
#         worsened, or fluctuated.
#         4. Do not infer information that is not present.


#         RESPONSE REQUIREMENTS

#         For questions involving comparison of laboratory results:

#         1. Start with a direct answer to the user's question.

#         2. Identify the relevant laboratory tests and compare their
#         actual values chronologically.

#         3. For every relevant test, show:
#         - test name
#         - date
#         - value
#         - unit
#         - change from the previous available report

#         4. Explain the direction of change in plain language:
#         - Improved
#         - Worsened
#         - Fluctuating
#         - Stable
#         - Insufficient Data

#         5. When possible, calculate the numerical change between
#         consecutive measurements.

#         6. Do not only say "improved" or "worsened".
#         Explain what changed using the actual values.

#         7. If the report contains a reference range, mention whether
#         the latest value is within or outside that report's
#         reference range.

#         8. Do not invent a reference range when one is not available.

#         9. Clearly distinguish between:
#         - change in a laboratory value
#         - interpretation of that change
#         - diagnosis or disease progression

#         10. Use simple language that a patient can understand.

#         11. Avoid unnecessary medical terminology. If a medical term
#             is necessary, briefly explain it.

#         12. Do not overwhelm the user with unrelated tests.
#             Only include tests relevant to the question.

#         13. If the available information is insufficient, explicitly
#             state what information is missing.

#         14. End with a short "Bottom line" statement answering the
#             user's original question.

#         Patient information:

#         {patient_history}

#         User question:

#         {question}

#         Provide a concise, evidence-grounded answer.
#         """

from backend.history.history_builder import PatientHistoryService
from backend.qa.comparison_engine import ComparisonEngine


class PatientQAService:

    def __init__(self, db, llm):
        self.db = db
        self.llm = llm
        self.history_service = PatientHistoryService(db)
        self.comparison_engine = ComparisonEngine()

    def answer_question(self, patient_id: int, question: str):

        # ---------------------------------------------------------
        # Get patient's longitudinal history
        # ---------------------------------------------------------
        patient_history = self.history_service.build(patient_id)

        # ---------------------------------------------------------
        # Extract reports from patient history
        # ---------------------------------------------------------
        reports = patient_history.get("reports", [])

        # ---------------------------------------------------------
        # comparison test identification
        # ---------------------------------------------------------
        test_name = self._identify_test(question, reports)
        if test_name:
            comparison = self.comparison_engine.compare_test(reports=reports, test_name=test_name)
            evidence = { "comparison": comparison }
        else:
            evidence = patient_history

        # ---------------------------------------------------------
        # Call the LLM with the prompt and patient history
        # ---------------------------------------------------------
        prompt = self._build_prompt(question=question, patient_history=evidence)
        response = self.llm.invoke(prompt)
        return response.content

    # =============================================================
    # TEST IDENTIFICATION
    # =============================================================

    
    def _identify_test(self, question, reports):

        """
        Ask the LLM which laboratory test the patient is asking
        about.

        This replaces the hardcoded test_keywords dictionary.

        The LLM is NOT responsible for calculating changes.
        It only identifies the relevant test name.

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

        response = self.llm.invoke(identification_prompt)
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
    # PROMPT
    # =============================================================

    def _build_prompt(self, question, patient_history):

        return f"""
        You are a medical information assistant.

        Answer the user's question using ONLY the patient information provided below.

        Do not invent:
        - diagnoses
        - laboratory values
        - dates
        - medications
        - treatments
        - clinical history

        If the available patient information does not
        contain enough evidence to answer the question,
        clearly say that the available data is insufficient.

        When comparing laboratory values:

        1. Use the actual dates.
        2. Use the actual values.
        3. Mention whether the value improved,
        worsened, or fluctuated.
        4. Do not infer information that is not present.


        RESPONSE REQUIREMENTS

        For questions involving comparison of laboratory results:

        1. Start with a direct answer to the user's question.

        2. Identify the relevant laboratory tests and compare their
        actual values chronologically.

        3. For every relevant test, show:
        - test name
        - date
        - value
        - unit
        - change from the previous available report

        4. Explain the direction of change in plain language:
        - Improved
        - Worsened
        - Fluctuating
        - Stable
        - Insufficient Data

        5. When possible, calculate the numerical change between
        consecutive measurements.

        6. Do not only say "improved" or "worsened".
        Explain what changed using the actual values.

        7. If the report contains a reference range, mention whether
        the latest value is within or outside that report's
        reference range.

        8. Do not invent a reference range when one is not available.

        9. Clearly distinguish between:
        - change in a laboratory value
        - interpretation of that change
        - diagnosis or disease progression

        10. Use simple language that a patient can understand.

        11. Avoid unnecessary medical terminology. If a medical term
            is necessary, briefly explain it.

        12. Do not overwhelm the user with unrelated tests.
            Only include tests relevant to the question.

        13. If the available information is insufficient, explicitly
            state what information is missing.

        14. End with a short "Bottom line" statement answering the
            user's original question.

        Patient information:

        {patient_history}

        User question:

        {question}

        Provide a concise, evidence-grounded answer.
        """