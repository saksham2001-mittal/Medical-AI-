from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(
    model="gemma4:31b-cloud",
    temperature=0,
)

def invoke(prompt):
    """
    Centralized LLM invocation.
    """
    return llm.invoke(prompt)