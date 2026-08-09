from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(
    model="gemma4:31b-cloud",
    # model= "qwen3.5:4b",
    temperature=0,
)

def invoke(prompt):
    """
    Centralized LLM invocation.
    """
    return llm.invoke(prompt)