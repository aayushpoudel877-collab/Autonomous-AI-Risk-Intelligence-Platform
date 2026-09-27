import json
import sqlite3
from pathlib import Path

import numpy as np

from ml.intelligence.documents import DocumentChunk


class SQLiteVectorStore:
    """Durable local vector store using SQLite and serialized normalized vectors."""

    def __init__(self, path, provider):
        self.path = str(path)
        self.provider = provider
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS vector_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    source TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    vector TEXT NOT NULL,
                    dimensions INTEGER NOT NULL
                )
                """
            )

    def _connect(self):
        return sqlite3.connect(self.path)

    def add(self, chunks):
        chunks = list(chunks)
        if not chunks:
            return
        vectors = self.provider.encode([chunk.text for chunk in chunks])
        if vectors.shape != (len(chunks), self.provider.dimensions):
            raise ValueError("embedding provider returned an unexpected shape")
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO vector_chunks
                (chunk_id, document_id, text, source, metadata, vector, dimensions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        chunk.chunk_id,
                        chunk.document_id,
                        chunk.text,
                        chunk.source,
                        json.dumps(chunk.metadata, sort_keys=True),
                        json.dumps(vector.tolist()),
                        self.provider.dimensions,
                    )
                    for chunk, vector in zip(chunks, vectors)
                ],
            )

    def count(self):
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM vector_chunks").fetchone()[0])

    def document_count(self):
        with self._connect() as connection:
            return int(
                connection.execute("SELECT COUNT(DISTINCT document_id) FROM vector_chunks").fetchone()[0]
            )

    def search(self, query, top_k=5):
        if top_k < 1:
            raise ValueError("top_k must be positive")
        query_vector = self.provider.encode([query])[0]
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT chunk_id, document_id, text, source, metadata, vector, dimensions "
                "FROM vector_chunks"
            ).fetchall()
        scored = []
        for row in rows:
            if row[6] != self.provider.dimensions:
                continue
            vector = np.asarray(json.loads(row[5]), dtype=float)
            score = float(vector @ query_vector)
            if score > 0:
                chunk = DocumentChunk(
                    document_id=row[1],
                    chunk_id=row[0],
                    text=row[2],
                    source=row[3],
                    metadata=json.loads(row[4]),
                )
                scored.append((chunk, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]
