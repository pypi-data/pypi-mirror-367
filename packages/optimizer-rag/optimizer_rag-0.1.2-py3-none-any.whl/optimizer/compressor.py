import os
from dotenv import load_dotenv
from .token_utils import num_tokens_from_string
from .selector import select_chunks_within_budget
from .scorer import score_chunks_tfidf

load_dotenv()

DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"

_default_client = None
if os.getenv("GROQ_API_KEY"):
    from groq import Groq
    _default_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def summarize_chunk_with_groq(chunk: str, query: str, model=DEFAULT_GROQ_MODEL, client=None) -> str:
    if client is None:
        if _default_client is None:
            raise ValueError("Groq client must be passed explicitly if GROQ_API_KEY is not set.")
        client = _default_client

    prompt = (
        f"Summarize the following document chunk focusing on answering this query:\n"
        f"Query: {query}\n"
        f"Chunk: {chunk}\n\n"
        f"Provide a concise but informative summary:"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=256,
    )

    return response.choices[0].message.content.strip()


def compress_chunk(chunks: list[str], query: str, token_budget: int, model=DEFAULT_GROQ_MODEL, client=None) -> list[str]:
    scored_chunks = score_chunks_tfidf(query, chunks)
    selected_chunks = select_chunks_within_budget(scored_chunks, token_limit=token_budget, model=model)
    summarized_chunks = []
    for chunk in selected_chunks:
        summary = summarize_chunk_with_groq(chunk, query, model=model, client=client)
        summarized_chunks.append(summary)
    return summarized_chunks