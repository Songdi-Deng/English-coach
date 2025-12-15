# rag.py
import os
import re
from typing import List

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Folder where you put your course books (PDFs or .txt)
DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")


def _read_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


def _read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    """
    Very simple word-based chunking.
    chunk_size ≈ number of words per chunk.
    overlap keeps some context between chunks.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += max(1, chunk_size - overlap)
    return chunks


def _load_all_chunks() -> List[str]:
    if not os.path.isdir(DOCS_DIR):
        return []

    chunks: List[str] = []
    for fname in os.listdir(DOCS_DIR):
        path = os.path.join(DOCS_DIR, fname)
        if not os.path.isfile(path):
            continue

        text = ""
        lower = fname.lower()
        try:
            if lower.endswith(".pdf"):
                text = _read_pdf(path)
            elif lower.endswith(".txt"):
                text = _read_txt(path)
        except Exception as e:
            print(f"[RAG] Error reading {fname}: {e}")
            continue

        cleaned = _clean_text(text)
        if cleaned:
            chunks.extend(_chunk_text(cleaned))

    return chunks


# ====== Build the index once on import ======
ALL_CHUNKS: List[str] = _load_all_chunks()

if ALL_CHUNKS:
    print(f"[RAG] Loaded {len(ALL_CHUNKS)} chunks from course books.")
    _vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    _doc_vectors = _vectorizer.fit_transform(ALL_CHUNKS)
else:
    print("[RAG] No documents found in 'documents' folder.")
    _vectorizer = None
    _doc_vectors = None


def get_relevant_context(query: str, k: int = 4) -> str:
    """
    Return a string with the k most relevant chunks for the given query.
    If there are no docs, returns empty string.
    """
    if _vectorizer is None or _doc_vectors is None or not ALL_CHUNKS:
        return ""

    q_vec = _vectorizer.transform([query])
    sims = cosine_similarity(q_vec, _doc_vectors)[0]

    # Highest similarity first
    top_idx = sims.argsort()[::-1][:k]
    selected = []
    for i in top_idx:
        if sims[i] <= 0:
            continue
        selected.append(ALL_CHUNKS[i])

    if not selected:
        return ""

    return "\n\n---\n\n".join(selected)
