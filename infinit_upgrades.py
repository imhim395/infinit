"""
infinit_upgrades.py
====================
Drop-in helper module for the Infinit AI backend.
Import this in server.py and wire up the functions below.
Nothing in your existing code needs to be deleted.
"""

import re
import httpx
from typing import AsyncGenerator

# ─────────────────────────────────────────────
# 1. QUERY CLASSIFIER
# ─────────────────────────────────────────────

CLASSIFY_PROMPT = """You are a query classifier. Classify the user query into EXACTLY one of:
factual_question | research_question | math_problem | explanation | coding_question

Reply with ONLY the category label, nothing else.

Query: {question}
Category:"""

async def classify_query(question: str, ollama_url: str, model: str) -> str:
    """
    Classifies a user query into one of five types using the local LLM.
    Returns one of: factual_question, research_question, math_problem,
                    explanation, coding_question
    Falls back to 'factual_question' on any error.
    """
    valid_types = {
        "factual_question", "research_question",
        "math_problem", "explanation", "coding_question"
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": CLASSIFY_PROMPT.format(question=question),
                    "stream": False,
                    "options": {"temperature": 0, "num_predict": 10},
                },
            )
            raw = resp.json().get("response", "").strip().lower()
            # Accept partial matches (model might add punctuation)
            for vt in valid_types:
                if vt in raw:
                    return vt
    except Exception:
        pass
    return "factual_question"


# ─────────────────────────────────────────────
# 2. SMART SEARCH TRIGGER
# ─────────────────────────────────────────────

# Keywords that force a search regardless of query type
RECENCY_KEYWORDS = {
    "latest", "current", "news", "today", "tonight",
    "2024", "2025", "2026", "recently", "just announced",
    "this week", "this month", "right now", "live",
}

def should_trigger_search(question: str, query_type: str) -> bool:
    """
    Returns True when Tavily search should be triggered.
    Triggers on: research/factual query types, or recency keywords.
    """
    if query_type in ("research_question", "factual_question"):
        return True
    lowered = question.lower()
    return any(kw in lowered for kw in RECENCY_KEYWORDS)


# ─────────────────────────────────────────────
# 3. SOURCE CITATIONS  (prompt builder)
# ─────────────────────────────────────────────

def build_cited_prompt(question: str, search_results: list[dict]) -> tuple[str, list[str]]:
    """
    Builds a prompt that instructs the LLM to cite sources inline [1][2]…
    Returns (prompt_string, list_of_source_urls).
    search_results: list of dicts with at least {"url": ..., "content": ...}
    Limits to first 3 sources.
    """
    sources = search_results[:3]
    source_urls = [s.get("url", "") for s in sources]

    context_blocks = []
    for i, src in enumerate(sources, start=1):
        snippet = src.get("content", "")[:600]   # keep prompt compact
        context_blocks.append(f"[{i}] {src.get('url', '')}\n{snippet}")

    context_str = "\n\n".join(context_blocks)

    prompt = f"""Answer the following question using the sources below.
After each factual claim, add an inline citation like [1] or [2].
At the end, list all sources used under a "Sources:" heading.

Question: {question}

Sources:
{context_str}

Answer:"""

    return prompt, source_urls


# ─────────────────────────────────────────────
# 4. ANSWER VERIFICATION PASS
# ─────────────────────────────────────────────

VERIFY_PROMPT = """You are a fact-checker. Review the answer below against the provided sources.
- If the answer contains factual errors, correct them and return the improved answer.
- If the answer is accurate, return it unchanged.
- Do NOT add new information beyond what the sources support.
- Do NOT change the citation markers [1][2]…

Sources:
{sources}

Answer to verify:
{answer}

Verified answer:"""

async def verify_answer(
    answer: str,
    source_texts: list[str],
    ollama_url: str,
    model: str,
) -> tuple[str, bool]:
    """
    Runs a second LLM pass to fact-check the answer against sources.
    Returns (verified_answer, was_corrected).
    """
    if not source_texts:
        return answer, False

    sources_str = "\n\n".join(source_texts[:3])
    prompt = VERIFY_PROMPT.format(sources=sources_str, answer=answer)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 1024},
                },
            )
            verified = resp.json().get("response", "").strip()
            was_corrected = verified.lower() != answer.lower()
            return verified if verified else answer, was_corrected
    except Exception:
        return answer, False


# ─────────────────────────────────────────────
# 5. CONFIDENCE SCORE
# ─────────────────────────────────────────────

UNCERTAINTY_PHRASES = [
    "i'm not sure", "i am not sure", "uncertain", "i don't know",
    "i do not know", "not certain", "unclear", "may be incorrect",
    "i cannot confirm",
]

def compute_confidence(
    answer: str,
    sources_used: list,
    verification_made_corrections: bool,
) -> int:
    """
    Returns a confidence score 0–100 based on simple heuristics.
    +30  web sources were used
    +20  multiple (2+) sources support the answer
    +20  verification pass found no corrections
    -20  answer contains uncertainty phrases
    """
    score = 30  # baseline

    if sources_used:
        score += 30
    if len(sources_used) >= 2:
        score += 20
    if not verification_made_corrections:
        score += 20

    answer_lower = answer.lower()
    if any(phrase in answer_lower for phrase in UNCERTAINTY_PHRASES):
        score -= 20

    return max(0, min(100, score))


# ─────────────────────────────────────────────
# 6. PROGRESS STREAMING  (SSE helper)
# ─────────────────────────────────────────────

async def stream_progress(message: str) -> str:
    """
    Returns a Server-Sent Events (SSE) progress chunk.
    Yield this from your streaming endpoint before the main answer tokens.

    Usage in your FastAPI route:
        yield stream_progress("🔎 Searching the web...")
    """
    return f"data: {{\"type\":\"progress\",\"message\":\"{message}\"}}\n\n"


# ─────────────────────────────────────────────
# 7. STRUCTURED RESPONSE BUILDER
# ─────────────────────────────────────────────

def build_response(
    answer: str,
    sources: list[str],
    confidence: int,
    tools_used: list[str],
) -> dict:
    """
    Wraps the final answer in the standard Infinit response envelope.
    {
        "answer": "...",
        "sources": [...],
        "confidence": 0-100,
        "tools_used": ["search", "memory"]
    }
    """
    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "tools_used": tools_used,
    }
