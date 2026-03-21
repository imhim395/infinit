from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from VectorV1 import retriever

model = OllamaLLM(model = "mathstral:7b")

template = """
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model


while True:
    print("\n\n-----------------------------------------------")
    question = input("What would you like to ask? (q to quit): ")
    print("\n\n")
    if question == "q":
        break

    info = retriever.invoke(question)
    for chunk in chain.stream({"question": question}):
        print(chunk, end="", flush=True)