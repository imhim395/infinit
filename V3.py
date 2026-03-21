from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM

# 1️⃣ Load embeddings & vector DB
embeddings = OllamaEmbeddings(model="nomic-embed-text")

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# 2️⃣ Load your LLM
llm = OllamaLLM(model="mathstral:7b")  # replace with your model name


# 3️⃣ Helper function using a formatted string instead of PromptTemplate
def ask(question):
    # Use vectorstore.similarity_search() instead of retriever
    docs = vectorstore.similarity_search(question, k=4)  # top 4 chunks

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are a K-8 science assistant.
Use ONLY the context below to answer the question.
If the answer is not in the context, come up with an estimated guess, but make sure to tell the person that you are coming up with a estimated guess
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
Context:
{context}

Question:
{question}

Answer:
"""
    return llm.invoke(prompt)
# 4️⃣ Chat loop
while True:
    q = input("Ask me a science question: ")
    print(ask(q))
