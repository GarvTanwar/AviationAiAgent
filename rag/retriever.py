from typing import List, Dict

import numpy as np

from rag.embedder import EmbeddingService
from rag.vector_store import FAISSVectorStore


class RAGRetriever:
    def __init__(self, store_dir: str = "rag_store") -> None:
        self.embedder = EmbeddingService()
        self.vector_store = FAISSVectorStore(store_dir=store_dir)
        self.index = self.vector_store.load_index()
        self.metadata = self.vector_store.load_metadata()

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        if self.index is None or not self.metadata:
            return []

        query_vector = self.embedder.embed_query(query).astype("float32").reshape(1, -1)
        distances, indices = self.index.search(query_vector, top_k)

        results = []

        for rank, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue

            item = self.metadata[idx].copy()
            item["score"] = float(distances[0][rank])
            results.append(item)

        return results