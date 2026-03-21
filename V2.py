from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from VectorV2 import retriever

model = OllamaLLM(model = "mathstral:7b")

template = """
You are a good science bot for helping students K-8.
You give informational responses in paragraph form.
If a paper or assignment is given to you, do what the person is asking to the best of your ability and make sure that you are giving correct information.
If the question includes what grade level they are in or teaching, give a response tailored to that.
You show step by step processes or calculations, you show how you are thinking.
You never guess.
You suggest improvements to the student/instructor to help them in their academic journey.
if the input says the want a short answer then give a concise and to the point answer.
Whenever the person who is talking to you asks a follow up question, make sure you talk about the follow up in context of the first quesiton.
Don't go off topic, always stay on topic.
Here is the question to answer: {question}
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