from abc import ABC, abstractmethod
from hashlib import sha256

import numpy as np


class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def dimensions(self):
        """Return the fixed embedding dimension."""

    @abstractmethod
    def encode(self, texts):
        """Encode a sequence of texts into row-normalized vectors."""


class HashEmbeddingProvider(EmbeddingProvider):
    """Deterministic, dependency-light fallback embedding provider.

    This is a lexical hashing baseline, not a semantic language model.
    """

    def __init__(self, dimensions=128):
        if dimensions < 1:
            raise ValueError("dimensions must be positive")
        self._dimensions = dimensions

    @property
    def dimensions(self):
        return self._dimensions

    def encode(self, texts):
        vectors = []
        for text in texts:
            vector = np.zeros(self.dimensions, dtype=float)
            for token in text.lower().split():
                digest = sha256(token.encode("utf-8")).digest()
                bucket = int.from_bytes(digest[:8], "big") % self.dimensions
                vector[bucket] += 1.0
            norm = np.linalg.norm(vector)
            vectors.append(vector / norm if norm else vector)
        return np.asarray(vectors)


class RetrievalIndex:
    def __init__(self, provider=None):
        self.provider = provider or HashEmbeddingProvider()
        self.chunks = []
        self.vectors = np.empty((0, self.provider.dimensions))

    def add(self, chunks):
        chunks = list(chunks)
        if not chunks:
            return
        encoded = self.provider.encode([chunk.text for chunk in chunks])
        if encoded.shape != (len(chunks), self.provider.dimensions):
            raise ValueError("embedding provider returned an unexpected shape")
        self.chunks.extend(chunks)
        self.vectors = np.vstack([self.vectors, encoded])

    def search(self, query, top_k=5):
        if top_k < 1:
            raise ValueError("top_k must be positive")
        if not self.chunks:
            return []
        query_vector = self.provider.encode([query])[0]
        scores = self.vectors @ query_vector
        order = np.argsort(-scores, kind="stable")[:top_k]
        return [
            (self.chunks[i], float(scores[i]))
            for i in order
            if scores[i] > 0
        ]
