"""Turns text into numbers ("embeddings") so the computer can compare meaning.

Two sentences with similar meaning get similar numbers, even if the words differ.
That is what lets us search by meaning instead of exact keywords.
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from .config import EMBED_MODEL


@lru_cache(maxsize=1)
def get_model():
    # First run downloads the model (~90 MB). After that it is cached.
    return SentenceTransformer(EMBED_MODEL)


def embed(texts):
    """Takes a list of strings, returns a list of number-lists."""
    return get_model().encode(texts, normalize_embeddings=True).tolist()
