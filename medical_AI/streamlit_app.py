# ==================================================================
# ==================== Medical AI Assistant ==========================
# ==================================================================

import streamlit as st

from backend.agentic_qa.service import AgenticPatientQAService
from backend.database.connections import SessionLocal


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🩺",
    layout="wide",
)


# ---------------------------------------------------------
# Application title
# ---------------------------------------------------------

st.title("🩺 Medical AI Assistant")

st.caption(
    "Ask questions about your medical reports and compare "
    "your laboratory results over time."
)


# ---------------------------------------------------------
# Patient name
# ---------------------------------------------------------

patient_name = st.text_input(
    "Patient Name",
    placeholder="Enter your patient name",
)


# ---------------------------------------------------------
# Initialize chat history
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------
# Display previous messages
# ---------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------------------------------------------------
# Chat input
# ---------------------------------------------------------

if question := st.chat_input(
    "Ask a question about your medical reports..."
):

    # -----------------------------------------------------
    # Validate patient name
    # -----------------------------------------------------

    if not patient_name.strip():

        st.error("Please enter your patient name.")

    else:

        # -------------------------------------------------
        # Display user question
        # -------------------------------------------------

        with st.chat_message("user"):
            st.markdown(question)

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        # -------------------------------------------------
        # Database session
        # -------------------------------------------------

        db = SessionLocal()

        try:

            with st.chat_message("assistant"):

                with st.spinner(
                    "Analyzing your medical reports..."
                ):

                    # -------------------------------------
                    # Create QA service
                    # -------------------------------------

                    service = AgenticPatientQAService(db)

                    # -------------------------------------
                    # Run LangGraph
                    # -------------------------------------

                    answer = service.answer_question(
                        patient_name=patient_name.strip(),
                        question=question.strip(),
                    )

                # -----------------------------------------
                # Display answer
                # -----------------------------------------

                st.markdown(answer)

            # ---------------------------------------------
            # Save answer to chat history
            # ---------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        except Exception as e:

            error_message = (
                "Sorry, I was unable to process your question."
            )

            with st.chat_message("assistant"):
                st.error(error_message)

                # Useful during development
                st.exception(e)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )

        finally:

            # ---------------------------------------------
            # Always close DB session
            # ---------------------------------------------

            db.close()