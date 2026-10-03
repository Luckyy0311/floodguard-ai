import json
import numpy as np

from pathlib import Path
from sentence_transformers import SentenceTransformer

from .config import DOCS_DIR, VECTOR_DIR


class SimpleVectorStore:
    """
    Lightweight RAG store using Sentence Transformers and NumPy.
    """

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

        self.embedding_file = VECTOR_DIR / "embeddings.npy"
        self.meta_file = VECTOR_DIR / "chunks.json"

        self.chunks = []
        self.embeddings = None

    def _chunk_text(self, text, source, chunk_size=700, overlap=120):
        text = " ".join(text.split())

        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]

            if len(chunk.strip()) > 50:
                chunks.append({
                    "text": chunk,
                    "source": source
                })

            if end == len(text):
                break

            start = end - overlap

        return chunks

    def load_documents(self):
        if not DOCS_DIR.exists():
            return []

        chunks = []

        for file_path in sorted(DOCS_DIR.glob("*.txt")):
            text = file_path.read_text(encoding="utf-8")
            chunks.extend(self._chunk_text(text, file_path.name))

        return chunks

    def build(self):
        VECTOR_DIR.mkdir(parents=True, exist_ok=True)

        self.chunks = self.load_documents()

        if not self.chunks:
            self.chunks = [{
                "text": "No preparedness documents found.",
                "source": "system"
            }]

        texts = [chunk["text"] for chunk in self.chunks]

        self.embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        np.save(self.embedding_file, self.embeddings)
        self.meta_file.write_text(
            json.dumps(self.chunks, indent=2),
            encoding="utf-8"
        )

        return len(self.chunks)

    def load(self):
        if self.embedding_file.exists() and self.meta_file.exists():
            self.embeddings = np.load(self.embedding_file)
            self.chunks = json.loads(
                self.meta_file.read_text(encoding="utf-8")
            )
            return True

        return False

    def load_or_build(self):
        if not self.load():
            self.build()

    def search(self, query, k=3):
        self.load_or_build()

        if not self.chunks or self.embeddings is None:
            return [{
                "text": "No knowledge base available.",
                "source": "system",
                "score": 0.0
            }]

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )[0]

        scores = self.embeddings @ query_embedding
        top_indexes = np.argsort(scores)[::-1][:k]

        results = []

        for index in top_indexes:
            results.append({
                "text": self.chunks[index]["text"],
                "source": self.chunks[index]["source"],
                "score": float(scores[index])
            })

        return results