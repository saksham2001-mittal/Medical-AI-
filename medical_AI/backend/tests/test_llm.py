from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="gemma4:31b-cloud",
    temperature=0,
)

response = llm.invoke("Say hello in one sentence.")

print(response)