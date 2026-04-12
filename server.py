from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Iterator
import datetime
import re
import importlib
import requests

# Load environment variables from .env file
from dotenv import load_dotenv
import os
load_dotenv()

# Heavy V3/V4 resources are initialized lazily so lightweight routes like
# /models can still start even when vector backends
# are unavailable in the current environment.
_retriever_v1 = None
_retriever_v2 = None
_chain_v1 = None
_chain_v2 = None
_vectorstore_v3 = None
_llm_v3 = None
_vectorstore_v4 = None
_llm_v4 = None
_tavily = None


def _get_retriever_v1():
    global _retriever_v1
    if _retriever_v1 is None:
        _retriever_v1 = importlib.import_module("VectorV1").retriever
    return _retriever_v1


def _get_retriever_v2():
    global _retriever_v2
    if _retriever_v2 is None:
        _retriever_v2 = importlib.import_module("VectorV2").retriever
    return _retriever_v2


def _get_v3_vectorstore():
    global _vectorstore_v3
    if _vectorstore_v3 is None:
        from langchain_ollama import OllamaEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
        import pandas as pd
        
        embeddings_v3 = OllamaEmbeddings(model="nomic-embed-text")
        _vectorstore_v3 = Chroma(
            persist_directory="ChromaDB_V2V3",
            collection_name="Science_RAG_DB",
            embedding_function=embeddings_v3,
        )
    return _vectorstore_v3


def _get_v3_llm():
    global _llm_v3
    if _llm_v3 is None:
        from langchain_ollama.llms import OllamaLLM
        _llm_v3 = OllamaLLM(model="mathstral:7b")
    return _llm_v3


def _get_v4_vectorstore():
    global _vectorstore_v4
    if _vectorstore_v4 is None:
        from langchain_ollama import OllamaEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
        import os
        import pandas as pd
        
        embeddings_v4 = OllamaEmbeddings(model="nomic-embed-text")
        db_location_v4 = "ChromaDB_V4"
        
        # Check if we need to load documents from CSV
        if not os.path.exists(db_location_v4):
            print("[V4] Building STEM K-12 database from stem_k12_rag_dataset.csv...")
            df = pd.read_csv("stem_k12_rag_dataset.csv")
            documents = []
            ids = []
            
            print(f"[V4] Processing {len(df)} documents...")
            for i, row in df.iterrows():
                document = Document(
                    page_content=f"Topic: {row['topic']} | Subject: {row['subject']} | Grade: {row['grade_level']} ({row['grade_band']}) | Domain: {row['domain']} | Subtopic: {row['subtopic']} | Learning Objective: {row['learning_objective']} | Concept Explanation: {row['concept_explanation']} | Worked Example: {row['worked_example']} | Misconception: {row['misconception_clarification']} | Real-World Application: {row['real_world_application']} | Standards: {row['ngss_standard']}, {row['ccss_standard']}, {row['csta_standard']}",
                    id=str(i)
                )
                ids.append(str(i))
                documents.append(document)
                if (i + 1) % 1000 == 0:
                    print(f"[V4] Processed {i + 1}/{len(df)} documents...")
            
            print("[V4] Creating vector store...")
            _vectorstore_v4 = Chroma(
                persist_directory=db_location_v4,
                collection_name="STEM_K12_DB",
                embedding_function=embeddings_v4,
            )
            
            # Add documents in batches
            batch_size = 500
            total = len(documents)
            for batch_start in range(0, total, batch_size):
                batch_end = min(batch_start + batch_size, total)
                batch_docs = documents[batch_start:batch_end]
                batch_ids = ids[batch_start:batch_end]
                _vectorstore_v4.add_documents(documents=batch_docs, ids=batch_ids)
                print(f"[V4] Embedded {batch_end}/{total} documents...")
            print("[V4] Database complete!")
        else:
            _vectorstore_v4 = Chroma(
                persist_directory=db_location_v4,
                collection_name="STEM_K12_DB",
                embedding_function=embeddings_v4,
            )
    return _vectorstore_v4


def _get_v4_llm():
    global _llm_v4
    if _llm_v4 is None:
        from langchain_ollama.llms import OllamaLLM
        _llm_v4 = OllamaLLM(model="infinit-v4")
    return _llm_v4


def _get_tavily_client():
    global _tavily
    if _tavily is None:
        from tavily import TavilyClient
        _tavily = TavilyClient(api_key="not on github")
    return _tavily


def _get_chain_v1():
    global _chain_v1
    if _chain_v1 is None:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_ollama.llms import OllamaLLM
        _chain_v1 = ChatPromptTemplate.from_template(
            "Here is the question to answer: {question}"
        ) | OllamaLLM(model="mathstral:7b")
    return _chain_v1


def _get_chain_v2():
    global _chain_v2
    if _chain_v2 is None:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_ollama.llms import OllamaLLM
        _chain_v2 = ChatPromptTemplate.from_template(_template_v2) | OllamaLLM(model="mathstral:7b")
    return _chain_v2

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================================================================
# CONTENT FILTER
# ===========================================================================
_BLOCKED = [
    r"\b(porn|nude|naked|kill\s+people|murder|rape|drug\s+recipe|make\s+a\s+bomb|how\s+to\s+make\s+meth|suicide\s+method)\b",
]
def _is_inappropriate(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in _BLOCKED)

def _invoke_v1(question: str, **kw) -> str:
    _get_retriever_v1().invoke(question)
    return _get_chain_v1().invoke({"question": question})

def _stream_v1(question: str, **kw) -> Iterator[str]:
    _get_retriever_v1().invoke(question)
    yield from _get_chain_v1().stream({"question": question})

# ===========================================================================
# V2
# ===========================================================================
_template_v2 = """You are a good science bot for helping students K-8.
You give informational responses in paragraph form.
If a paper or assignment is given to you, do what the person is asking to the best of your ability and make sure that you are giving correct information.
If the question includes what grade level they are in or teaching, give a response tailored to that.
You show step by step processes or calculations, you show how you are thinking.
You never guess.
You suggest improvements to the student/instructor to help them in their academic journey.
If the input says they want a short answer then give a concise and to the point answer.
Whenever the person who is talking to you asks a follow up question, make sure you talk about the follow up in context of the first question.
Don't go off topic, always stay on topic.
Here is the question to answer: {question}"""

def _invoke_v2(question: str, **kw) -> str:
    _get_retriever_v2().invoke(question)
    return _get_chain_v2().invoke({"question": question})

def _stream_v2(question: str, **kw) -> Iterator[str]:
    _get_retriever_v2().invoke(question)
    yield from _get_chain_v2().stream({"question": question})

# ===========================================================================
# V3
# ===========================================================================

def _grade_instruction(grade_level: str) -> str:
    if grade_level == "k3":
        return """YOU ARE TALKING TO A 5-7 YEAR OLD CHILD. This is the most important rule: pretend you are a friendly cartoon character explaining something to a kindergartner.
STRICT RULES — break any of these and you fail:
- NEVER use these words or anything like them: molecule, atom, organism, atmosphere, photosynthesis, evaporation, condensation, gravity, energy, hypothesis, scientific, chemical, compound, reaction, process, system, structure, function, cell, nucleus, particle, wave, frequency, vibration, nitrogen, oxygen, carbon dioxide. Replace them with simple words (example: instead of "gravity" say "a magic pulling force that keeps us from floating away").
- ONLY use words a 5 year old uses every day.
- Write MAXIMUM 3-4 short sentences total. Do not write more.
- Every sentence must be simple enough for a kindergartner.
- Use one fun comparison to something kids love like puppies, pizza, toys, or cartoons.
- End with: "Fun fact for your friends:" followed by one super simple sentence."""
    elif grade_level == "46":
        return """The student is in grades 4-6 (ages 9-11). Use clear, straightforward language. You can introduce some scientific terms but always define them simply. Use real-world examples and encourage curiosity."""
    elif grade_level == "78":
        return """The student is in grades 7-8 (ages 12-14). Use proper scientific vocabulary. You can explain more complex concepts, show detailed calculations, and make connections between topics. Be thorough and academically rigorous."""
    return """Use clear, age-appropriate language suitable for K-8 students."""

def _build_prompt_v3(question: str, mode: str = "normal", grade_level: str = "") -> str:
    docs = _get_v3_vectorstore().similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])
    today = datetime.date.today().strftime("%B %d, %Y")
    grade_note = _grade_instruction(grade_level)

    if mode == "quiz":
        task = f"Generate exactly 3 multiple-choice quiz questions with 4 options each based on this topic. Mark the correct answer clearly.\nTopic: {question}"
    elif mode == "socratic":
        task = f"Use the Socratic method. Ask the student 2-3 guiding questions that lead them to discover the answer themselves. Do NOT give the answer directly.\nTopic: {question}"
    elif mode == "hint":
        task = f"The student is stuck. Give ONE concrete scaffolded hint — a clue or partial step — that nudges them forward without revealing the full answer. Then ask a single follow-up question to keep them thinking.\nTopic: {question}"
    else:
        task = f"Answer this question thoroughly: {question}"

    return f"""Today's date is {today}.
{grade_note}
Use the context below as your primary source. If the answer is not fully in the context, supplement with your knowledge but clearly say so.
Always respond in well-structured paragraphs. Be detailed and thorough.
Use analogies and real-world examples. Show step by step calculations in full detail.
You never guess without saying so.
At the end of every response (unless quiz or socratic mode), suggest one hands-on experiment the student can try at home.
{task}

Context:
{context}

Answer:
"""

def _invoke_v3(question: str, mode: str = "normal", grade_level: str = "", **kw) -> str:
    return _get_v3_llm().invoke(_build_prompt_v3(question, mode, grade_level))

def _stream_v3(question: str, mode: str = "normal", grade_level: str = "", **kw) -> Iterator[str]:
    yield from _get_v3_llm().stream(_build_prompt_v3(question, mode, grade_level))

# ===========================================================================
# V4 — fine-tuned Mathstral + RAG + Tavily + confidence + citations
# ===========================================================================

# ---------------------------------------------------------------------------
# SEARCH DECISION ENGINE
# These are topics where LLMs often sound confident but still get it wrong.
# We always search for these, regardless of RAG confidence.
# ---------------------------------------------------------------------------

# Questions containing any of these patterns always trigger a web search
_ALWAYS_SEARCH_PATTERNS = [
    # Recency / time-sensitive
    "latest", "recent", "news", "today", "tonight", "right now", "live",
    "this week", "this month", "last week", "last month", "just announced",
    "just found", "recently discovered", "new discovery", "breaking",
    "current year", "current date", "what year", "what month", "what day",
    "what date", "2024", "2025", "2026",
    # Specific factual lookups that LLMs frequently mis-recall
    "who discovered", "when was", "who invented", "how many",
    "what is the speed", "what is the mass", "what is the distance",
    "how far", "how long", "how tall", "how big", "how hot", "how cold",
    "what temperature", "boiling point", "melting point", "atomic number",
    "atomic mass", "half-life", "wavelength", "frequency",
    # Named entities (people, places, organisms, chemicals)
    "who is", "where is", "which planet", "which element", "which species",
    "which country", "which scientist", "named after", "classified as",
    # Stats / numbers — LLMs confabulate these
    "percent", "percentage", "population", "density", "gravity on",
    "diameter of", "radius of", "surface area", "volume of",
    # Scientific consensus questions
    "is it true that", "scientists say", "research shows", "studies show",
    "proven", "evidence for", "nasa says", "according to scientists",
]

# These domains always get a web search even if question doesn't match patterns
_ALWAYS_SEARCH_DOMAINS = [
    "astronomy", "space", "planet", "star", "galaxy", "universe", "comet",
    "black hole", "solar system", "orbit", "nasa", "satellite",
    "chemistry", "element", "compound", "molecule", "atom", "reaction",
    "periodic table", "isotope", "ion",
    "biology", "species", "organism", "taxonomy", "dna", "gene", "cell",
    "evolution", "fossil", "extinct", "animal", "plant",
    "physics", "force", "energy", "mass", "velocity", "acceleration",
    "quantum", "relativity", "wave", "particle",
    "climate", "temperature", "weather", "ocean", "atmosphere", "co2",
    "greenhouse", "ozone", "ecosystem",
    "medicine", "disease", "virus", "bacteria", "vaccine", "symptom",
    "human body", "organ", "bone", "muscle",
    "geology", "volcano", "earthquake", "rock", "mineral", "plate",
    "tectonic", "fossil fuel",
    "math", "formula", "equation", "calculate", "compute", "solve",
]

def _needs_web_search(question: str, context: str) -> bool:
    """
    Returns True when Tavily should be called.

    Triggers:
    1. RAG context is weak (< 100 chars or empty)
    2. Question contains a recency/factual keyword
    3. Question touches a high-risk domain (numbers, named facts, science topics)
       — these domains are where LLMs hallucinate even at high confidence
    """
    # Always search if RAG has nothing useful
    if not context.strip() or len(context.strip()) < 100:
        return True

    q = question.lower()

    # Always search if any recency/factual trigger word is present
    if any(t in q for t in _ALWAYS_SEARCH_PATTERNS):
        return True

    # Always search if question touches a high-risk science/fact domain
    if any(domain in q for domain in _ALWAYS_SEARCH_DOMAINS):
        return True

    return False


def _score_confidence(context: str, n_docs: int, used_web: bool, web_ctx: str) -> str:
    """
    Calibrated confidence — accounts for the fact that good RAG context
    alone does NOT guarantee accuracy on specific factual questions.
    Web verification raises confidence; missing web lowers it.
    """
    if used_web and web_ctx.strip():
        # Web search returned results — high confidence
        return "high"
    if not context.strip() or len(context.strip()) < 100:
        return "low"
    if n_docs >= 3 and len(context.strip()) > 500:
        # Good RAG coverage but no web check — medium, not high
        return "medium"
    if n_docs >= 2:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# VERIFICATION PASS
# After generating an initial answer, run a second lightweight LLM call that
# compares the answer against the web sources and flags/corrects any errors.
# ---------------------------------------------------------------------------

_VERIFY_PROMPT = """You are a science fact-checker for a K-8 education assistant.

Review the ANSWER below against the WEB SOURCES provided.
- If the answer contains any factual errors or numbers that conflict with the sources, correct them.
- If the answer is accurate, return it EXACTLY as-is without any changes.
- Do NOT add new content beyond what the sources support.
- Do NOT change the tone or structure of the answer.
- Keep your response to only the corrected (or unchanged) answer text — no preamble.

WEB SOURCES:
{sources}

ANSWER TO CHECK:
{answer}

VERIFIED ANSWER:"""

def _verification_pass(answer: str, web_ctx: str) -> tuple[str, bool]:
    """
    Runs a second LLM pass to cross-check the answer against web sources.
    Returns (verified_answer, was_corrected).
    Only runs when web context is available.
    """
    if not web_ctx or not web_ctx.strip():
        return answer, False

    prompt = _VERIFY_PROMPT.format(
        sources=web_ctx[:2000],   # cap to keep prompt lean
        answer=answer,
    )
    try:
        verified = _get_v4_llm().invoke(prompt).strip()
        if not verified:
            return answer, False
        was_corrected = verified.lower() != answer.lower()
        return verified, was_corrected
    except Exception:
        return answer, False


def _get_v4_context(question: str):
    """Returns (rag_ctx, web_ctx, sources, confidence, used_web)."""
    docs = _get_v4_vectorstore().similarity_search(question, k=3)
    rag_ctx = "\n\n".join([d.page_content for d in docs])
    sources, used_web, web_ctx = [], False, ""

    if _needs_web_search(question, rag_ctx):
        try:
            res = _get_tavily_client().search(query=question, max_results=3)
            results = res.get("results", [])
            web_ctx = "\n\n".join([r.get("content", "") for r in results])
            sources = [
                {"title": r.get("title", ""), "url": r.get("url", "")}
                for r in results if r.get("url")
            ]
            used_web = True
        except Exception:
            pass

    confidence = _score_confidence(rag_ctx, len(docs), used_web, web_ctx)
    return rag_ctx, web_ctx, sources, confidence, used_web


def _build_footer(sources: list, confidence: str, used_web: bool, was_verified: bool) -> str:
    lines = [f"\n\n---\n**Confidence:** {confidence.upper()}"]
    lines.append("**Source:** Web Search + Knowledge Base" if used_web else "**Source:** Infinit Knowledge Base")
    if was_verified:
        lines.append("**✓ Verified:** Answer was cross-checked against web sources.")
    if sources:
        lines.append("**References:**")
        for s in sources:
            if s.get("url"):
                lines.append(f"- [{s.get('title', s['url'])}]({s['url']})")
    return "\n".join(lines)


def _build_prompt_v4(question: str, rag_ctx: str, web_ctx: str = "", mode: str = "normal", grade_level: str = "") -> str:
    today = datetime.date.today().strftime("%B %d, %Y")
    grade_note = _grade_instruction(grade_level)
    combined = rag_ctx + ("\n\nWeb Search Results:\n" + web_ctx if web_ctx else "")
    web_note = "\nNote: Some context below comes from a live web search — prioritize it for specific facts and numbers." if web_ctx else ""

    if mode == "quiz":
        task = f"Generate exactly 3 multiple-choice quiz questions with 4 options each based on this topic. Mark the correct answer clearly.\nTopic: {question}"
    elif mode == "socratic":
        task = f"Use the Socratic method. Ask the student 2-3 guiding questions that lead them to discover the answer themselves. Do NOT give the answer directly.\nTopic: {question}"
    elif mode == "hint":
        task = f"The student is stuck. Give ONE concrete scaffolded hint — a clue or a single partial step — that nudges them toward the answer without giving it away. Then ask one targeted question to keep their thinking going.\nTopic: {question}"
    else:
        task = f"Answer this question: {question}"

    return f"""<s>[INST]
You are a K-12 science assistant covering all grade levels from Kindergarten through AP courses.{web_note}
Today's date is {today}. Always use this when answering questions about the current year, month, or date.
The context below comes from a structured science database. Each entry may include:
- Grade Level and Difficulty (use these to calibrate your language and depth)
- Learning Objective (what the student should understand)
- Common Misconception (proactively correct this if relevant)
- Domain and Subtopic (stay focused on the relevant science area)
Use plain, age-appropriate language matched to the grade level in context.
Use the context below to answer. If the answer is not in the context, give your best answer but clearly say you are estimating.
Give informational responses in well-structured paragraphs.
Show step by step processes or calculations in full detail.
If a common misconception is present in the context and relevant to the question, explicitly address and correct it.
At the end of your response (unless quiz or socratic mode), always include ONE hands-on experiment or activity under a bold heading. Use this exact format:
**Try this at home:** followed by a simple, safe, age-appropriate experiment using common household items. Include: (1) materials needed, (2) step-by-step instructions, (3) what to observe, and (4) the science behind it.
Whenever the person asks a follow up question, answer in context of the previous question.
Do not go off topic.
{task}

Context:
{combined}

Answer:
[/INST]"""


def _invoke_v4(question: str, mode: str = "normal", **kw) -> str:
    rag_ctx, web_ctx, sources, confidence, used_web = _get_v4_context(question)

    # Pass 1: generate answer
    raw_answer = _get_v4_llm().invoke(_build_prompt_v4(question, rag_ctx, web_ctx, mode))

    # Pass 2: verify answer against web sources (only for normal answers, not quiz/socratic)
    if mode == "normal" and used_web:
        verified_answer, was_corrected = _verification_pass(raw_answer, web_ctx)
    else:
        verified_answer, was_corrected = raw_answer, False

    return verified_answer + _build_footer(sources, confidence, used_web, was_corrected)


def _stream_v4(question: str, mode: str = "normal", **kw) -> Iterator[str]:
    rag_ctx, web_ctx, sources, confidence, used_web = _get_v4_context(question)

    # For streaming: generate first, then verify, then stream the result token-by-token
    # (verification requires a complete answer first, so we collect then re-stream)
    raw_answer = ""
    for chunk in _get_v4_llm().stream(_build_prompt_v4(question, rag_ctx, web_ctx, mode)):
        raw_answer += chunk
        yield chunk

    # Pass 2: verify after streaming completes
    if mode == "normal" and used_web:
        verified_answer, was_corrected = _verification_pass(raw_answer, web_ctx)
        # If corrections were made, stream a correction notice + corrected answer
        if was_corrected:
            correction_block = (
                "\n\n---\n**📋 Correction Applied:** "
                "A fact-check pass found inaccuracies and corrected the answer above:\n\n"
                + verified_answer
            )
            yield correction_block
    else:
        was_corrected = False

    yield _build_footer(sources, confidence, used_web, was_corrected)


# ===========================================================================
# OFF-TOPIC GUARDIAN
# Gently redirects clearly non-STEM questions back to science topics.
# ===========================================================================
_STEM_ADJACENT = {
    "math", "science", "biology", "chemistry", "physics", "earth", "space",
    "planet", "star", "energy", "force", "cell", "atom", "element", "equation",
    "experiment", "volcano", "weather", "climate", "animal", "plant", "body",
    "brain", "heart", "dna", "gene", "gravity", "light", "sound", "wave",
    "rock", "mineral", "ocean", "ecosystem", "evolution", "fossil", "organ",
    "molecule", "reaction", "current", "electric", "magnet", "motion", "speed",
    "temperature", "pressure", "density", "mass", "weight", "force",
}

_OFF_TOPIC_SIGNALS = [
    "who won", "sports", "nfl", "nba", "soccer", "football", "basketball",
    "celebrity", "actor", "actress", "singer", "song", "lyrics", "movie",
    "game", "fortnite", "minecraft", "roblox", "tiktok", "instagram",
    "youtube", "meme", "funny", "joke", "prank", "social media",
    "politics", "president", "election", "war news", "stock", "crypto",
    "restaurant", "recipe", "food near me", "shopping",
]

def _is_off_topic(question: str) -> bool:
    q = question.lower()
    # If any STEM keyword is present, it's fair game
    if any(kw in q for kw in _STEM_ADJACENT):
        return False
    # If an off-topic signal appears and no science context, redirect
    return any(sig in q for sig in _OFF_TOPIC_SIGNALS)

_OFF_TOPIC_REPLY = (
    "Hey, great question — but Infinit is all about science, math, and STEM! 🚀 "
    "I'm not the best at {topic}-type questions. "
    "Want to explore something amazing instead? Try asking me about volcanoes, "
    "black holes, how your brain works, or anything else in the universe!"
)

def _off_topic_response(question: str) -> str:
    # Guess a rough topic from the question for the friendly message
    q = question.lower()
    if any(w in q for w in ["sports", "nfl", "nba", "soccer", "football", "basketball"]):
        topic = "sports"
    elif any(w in q for w in ["song", "music", "lyrics", "singer"]):
        topic = "music"
    elif any(w in q for w in ["game", "fortnite", "minecraft", "roblox"]):
        topic = "gaming"
    elif any(w in q for w in ["movie", "actor", "actress", "celebrity"]):
        topic = "entertainment"
    else:
        topic = "that"
    return _OFF_TOPIC_REPLY.format(topic=topic)


# ===========================================================================
# ANALYTICS ACCUMULATOR (in-memory, resets on server restart)
# ===========================================================================
from collections import Counter

_analytics: dict = {
    "total_questions": 0,
    "grade_counts": Counter(),
    "mode_counts": Counter(),
    "keyword_counts": Counter(),
}

_SCIENCE_KEYWORDS = [
    "volcano", "black hole", "cell", "atom", "dna", "gravity", "energy",
    "photosynthesis", "evolution", "planet", "climate", "weather", "force",
    "motion", "wave", "light", "sound", "rock", "ocean", "ecosystem",
    "brain", "heart", "organ", "gene", "molecule", "reaction", "element",
]

def _track_analytics(question: str, grade_level: str, mode: str):
    _analytics["total_questions"] += 1
    if grade_level:
        _analytics["grade_counts"][grade_level] += 1
    _analytics["mode_counts"][mode or "normal"] += 1
    q = question.lower()
    for kw in _SCIENCE_KEYWORDS:
        if kw in q:
            _analytics["keyword_counts"][kw] += 1


VERSIONS = {
    "v1": {"invoke": _invoke_v1, "stream": _stream_v1},
    "v2": {"invoke": _invoke_v2, "stream": _stream_v2},
    "v3": {"invoke": _invoke_v3, "stream": _stream_v3},
    "v4": {"invoke": _invoke_v4, "stream": _stream_v4},
}

# ===========================================================================
# Request model
# ===========================================================================
class ChatRequest(BaseModel):
    question: str
    model: str = "v4"
    file_content: str = ""
    mode: str = "normal"  # normal | quiz | socratic | hint
    grade_level: str = ""  # k3 | 46 | 78

def _inject_file(question: str, file_content: str) -> str:
    if not file_content.strip():
        return question
    return f"The user has uploaded a file with the following content:\n\n{file_content}\n\nUsing the file content above, answer this: {question}"

# ===========================================================================
# Routes
# ===========================================================================
@app.get("/models")
def list_models():
    return {"models": list(VERSIONS.keys())}

@app.get("/analytics")
def get_analytics():
    """Returns aggregate usage stats. No PII stored — topic frequency only."""
    top_keywords = _analytics["keyword_counts"].most_common(5)
    return {
        "total_questions": _analytics["total_questions"],
        "grade_distribution": dict(_analytics["grade_counts"]),
        "mode_distribution": dict(_analytics["mode_counts"]),
        "top_keywords": [{"keyword": k, "count": c} for k, c in top_keywords],
    }

@app.post("/chat/grade")
def chat_grade(req: ChatRequest):
    """
    Returns a grade-calibrated rephrasing of what the answer would focus on.
    Useful for teachers previewing how Infinit adapts to different levels.
    """
    grade_note = _grade_instruction(req.grade_level or "k3")
    prompt = (
        f"{grade_note}\n\n"
        f"In 2-3 sentences, explain how you would approach answering this question "
        f"for a student at the grade level above:\n\nQuestion: {req.question}"
    )
    try:
        answer = _get_v4_llm().invoke(prompt)
    except Exception:
        answer = _get_v3_llm().invoke(prompt)
    return {"grade_level": req.grade_level, "approach": answer.strip()}

@app.post("/chat")
def chat(req: ChatRequest):
    if req.model not in VERSIONS:
        raise HTTPException(status_code=400, detail=f"Unknown model version '{req.model}'")
    if _is_inappropriate(req.question):
        raise HTTPException(status_code=400, detail="This question is not appropriate for Infinit.")
    if _is_off_topic(req.question):
        return {"answer": _off_topic_response(req.question)}
    _track_analytics(req.question, req.grade_level, req.mode)
    combined = _inject_file(req.question, req.file_content)
    return {"answer": VERSIONS[req.model]["invoke"](combined, mode=req.mode, grade_level=req.grade_level)}

@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    if req.model not in VERSIONS:
        raise HTTPException(status_code=400, detail=f"Unknown model version '{req.model}'")
    if _is_inappropriate(req.question):
        raise HTTPException(status_code=400, detail="This question is not appropriate for Infinit.")
    if _is_off_topic(req.question):
        off_topic_msg = _off_topic_response(req.question)
        def _redirect():
            yield off_topic_msg
        return StreamingResponse(_redirect(), media_type="text/plain")
    _track_analytics(req.question, req.grade_level, req.mode)
    combined = _inject_file(req.question, req.file_content)

    def generate():
        yield from VERSIONS[req.model]["stream"](combined, mode=req.mode, grade_level=req.grade_level)

    return StreamingResponse(generate(), media_type="text/plain")

