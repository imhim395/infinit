"""
ingest_v4_database.py
=====================
Run this ONCE to load science_rag_database.csv into ChromaDB
as the new 'scibot_v4' collection used by Infinit V4.

Usage:
    python ingest_v4_database.py

Place this file in the same folder as server.py and science_rag_database.csv.
Requires: langchain-chroma, langchain-ollama, chromadb
"""

import csv
import os
import time
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# ── Config ────────────────────────────────────────────────────────────────────
CSV_PATH        = "./science_rag_database.csv"   # path to your new CSV
CHROMA_DIR      = "./chroma_db"                  # same dir as your existing DB
COLLECTION_NAME = "scibot_v4"                    # new collection name for V4
EMBED_MODEL     = "nomic-embed-text"             # must match what server.py uses
BATCH_SIZE      = 200                            # rows per ingestion batch
# ─────────────────────────────────────────────────────────────────────────────


def row_to_document(row: dict) -> Document:
    """
    Converts one CSV row into a LangChain Document.
    The page_content combines the most semantically rich fields so that
    similarity search works well.  Metadata keeps everything else for filtering.
    """
    # Build a rich text block that embeds well
    page_content = (
        f"Domain: {row['domain']}\n"
        f"Subtopic: {row['subtopic']}\n"
        f"Grade Level: {row['grade_level']}\n"
        f"Difficulty: {row['difficulty']}\n"
        f"Question Type: {row['question_type']}\n"
        f"Question: {row['question']}\n"
        f"Answer: {row['answer']}\n"
        f"Learning Objective: {row['learning_objective']}\n"
        f"Common Misconception: {row['common_misconception']}"
    )

    metadata = {
        "id":           row.get("id", ""),
        "domain":       row.get("domain", ""),
        "subtopic":     row.get("subtopic", ""),
        "grade_level":  row.get("grade_level", ""),
        "difficulty":   row.get("difficulty", ""),
        "question_type":row.get("question_type", ""),
        "standard":     row.get("standard", ""),
        "keywords":     row.get("keywords", ""),
    }

    return Document(page_content=page_content, metadata=metadata)


def load_csv(path: str) -> list[Document]:
    docs = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            docs.append(row_to_document(row))
    return docs


def ingest():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"CSV not found at '{CSV_PATH}'. "
            "Make sure science_rag_database.csv is in the same folder."
        )

    print(f"📂 Loading CSV from {CSV_PATH}...")
    docs = load_csv(CSV_PATH)
    print(f"   ✓ {len(docs):,} documents loaded.")

    print(f"\n🔌 Connecting to ChromaDB at '{CHROMA_DIR}' ...")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    # Create (or reuse) the new collection
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )

    # Check if collection already has data
    existing = vectorstore.get()
    if existing and len(existing.get("ids", [])) > 0:
        print(f"\n⚠️  Collection '{COLLECTION_NAME}' already has "
              f"{len(existing['ids']):,} documents.")
        answer = input("   Re-ingest and overwrite? [y/N]: ").strip().lower()
        if answer != "y":
            print("   Aborted. Existing collection unchanged.")
            return
        # Delete existing documents before re-ingesting
        vectorstore.delete_collection()
        vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
        )
        print("   Old collection cleared.")

    print(f"\n⚙️  Ingesting {len(docs):,} documents in batches of {BATCH_SIZE}...")
    total_batches = (len(docs) + BATCH_SIZE - 1) // BATCH_SIZE
    start = time.time()

    for i in range(0, len(docs), BATCH_SIZE):
        batch = docs[i : i + BATCH_SIZE]
        vectorstore.add_documents(batch)
        done = min(i + BATCH_SIZE, len(docs))
        elapsed = time.time() - start
        pct = done / len(docs) * 100
        print(f"   [{done:>6,}/{len(docs):,}]  {pct:5.1f}%  —  {elapsed:.0f}s elapsed")

    total = time.time() - start
    print(f"\n✅ Ingestion complete!")
    print(f"   Collection : '{COLLECTION_NAME}'")
    print(f"   Documents  : {len(docs):,}")
    print(f"   Time       : {total:.1f}s")
    print(f"\nℹ️  V4 in server.py already points to '{COLLECTION_NAME}'.")
    print("   Restart your server and V4 will use the new database automatically.")


if __name__ == "__main__":
    ingest()
