from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def score_chunks_tfidf(query: str, chunks: list[str]) -> list[tuple[str, float]]:
    """Return chunks with TF-IDF similarity scores to query."""
    documents = [query] + chunks
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()

    query_vec = vectors[0].reshape(1, -1)
    scores = cosine_similarity(query_vec, vectors[1:])[0]

    return list(zip(chunks, scores))