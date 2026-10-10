# MEDICAL AI ASSISTANT

An AI-powered medical report assistant that allows patients to upload their medical reports and ask questions about their health data.

The system is being designed to process medical reports, extract structured medical information, maintain patient history, and use an agentic AI workflow to analyze and compare medical data across reports.

## What We Are Building

The goal is to build an intelligent patient-facing medical assistant that can:

- Process and extract information from medical reports.
- Maintain a patient's historical medical data.
- Answer questions about individual test results.
- Compare current results with previous reports.
- Identify improving, worsening, fluctuating, and stable health parameters.
- Analyze the overall status of a patient's medical reports.
- Highlight persistent conditions and new or worsening findings.
- Use **RAG (Retrieval-Augmented Generation)** to retrieve relevant medical information and provide more contextual and grounded responses.
- Use **LangGraph-based agentic workflows** to route and process different types of patient questions.

## Architecture

The system combines:

- Structured medical data stored in PostgreSQL.
- Agentic workflows using LangGraph.
- LLM-based reasoning and response generation.
- RAG-based retrieval for contextual medical information.
- FastAPI for backend services.
- Streamlit for the patient-facing interface.

## Tech Stack

- Python
- LangChain
- LangGraph
- Ollama
- FastAPI
- Streamlit
- PostgreSQL
- SQLAlchemy
- Pydantic

## Project Status

🚧 **Under Development**

- The core medical report processing, patient history retrieval, report comparison, and agentic question-answering workflow have been implemented.

- RAG integration, report upload through the Streamlit interface, and additional improvements are planned as the project progresses.
