from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

df = pd.read_csv("DATA - Sheet1 (1) (1).csv")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

db_location = "CodingWithWindsurf"
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []

    for i, row in df.iterrows():
        document = Document(
            page_content=row["Grade"] + " " + row["Domain"] + " " + row["Key Concept"] + " " + row["Technical Depth & Detailed Explanation"],
            id=str(i)
        )
        ids.append(str(i))
        documents.append(document)

vector_store = Chroma(
    collection_name="Science_Information",
    persist_directory = db_location,
    embedding_function = embeddings,
)

if add_documents:
    vector_store.add_documents(documents = documents, ids = ids)

retriever = vector_store.as_retriever(
    search_kwargs={"k":3}
)