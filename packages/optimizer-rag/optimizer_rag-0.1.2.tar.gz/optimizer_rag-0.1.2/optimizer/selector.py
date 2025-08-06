from optimizer.token_utils import num_tokens_from_string

def select_chunks_within_budget(chunks_with_scores: list[tuple[str, float]], token_limit: int, model="llama-3.1-8b-instant"):
    """Sort by score, then select chunks that fit within the token limit."""
    selected = []
    total_tokens = 0

    chunks_with_scores.sort(key=lambda x: x[1], reverse=True)

    for chunk, score in chunks_with_scores:
        tokens = num_tokens_from_string(chunk, model=model)
        if total_tokens + tokens <= token_limit:
            selected.append(chunk)
            total_tokens += tokens
        else:
            break

    return selected