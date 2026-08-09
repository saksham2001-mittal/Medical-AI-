def build_patient_history_prompt(report_text: str) -> str:

    return f"""
        You are an expert clinical AI assistant.

        You will be given one or more medical reports belonging to the SAME patient.

        The reports are OCR extracted text, therefore they may contain:
        - Broken lines
        - OCR spelling mistakes
        - Split tables
        - Missing spaces
        - Duplicate information

        Your first task is to mentally reconstruct the report before extracting information.

        -------------------------
        REPORTS
        -------------------------

        {report_text}

        -------------------------
        YOUR TASK
        -------------------------

        Extract ONLY information that is explicitly present.

        Never assume.

        Never hallucinate.

        If a section is not available, return an empty list.

        Merge duplicate information across multiple reports.

        Return the response in the following JSON format only.

        {{
            "past_medical_history":[
                {{
                    "date":"",
                    "reason":""
                }}
            ],

            "medications":[
                {{
                    "name":"",
                    "dosage":"",
                    "frequency":""
                }}
            ],

            "allergies":[
                {{
                    "allergen":"",
                    "reaction":""
                }}
            ],

            "family_history":[
                {{
                    "relation":"",
                    "condition":""
                }}
            ],

            "social_history":{{
                "smoking_status":"",
                "alcohol_consumption":"",
                "diet_preference":"",
                "exercise_habits":""
            }},

            "preventive_health":[
                {{
                    "test":"",
                    "date":""
                }}
            ]
        }}

        Return ONLY valid JSON.

        Do not add explanations.

        Do not use markdown.
    """ 