from pathlib import Path
import json
import pickle
from typing import List, Dict

import faiss
import numpy as np


class FAISSVectorStore:
    def __init__(self, store_dir: str = "rag_store") -> None:
        self.store_path = Path(store_dir)
        self.store_path.mkdir(parents=True, exist_ok=True)

        self.index_path = self.store_path / "faiss.index"
        self.metadata_path = self.store_path / "metadata.json"
        self.embedding_path = self.store_path / "embeddings.pkl"

    def save(self, embeddings: np.ndarray, metadata: List[Dict]) -> None:
        if len(embeddings) == 0:
            raise ValueError("No embeddings to save.")

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype("float32"))

        faiss.write_index(index, str(self.index_path))

        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        with open(self.embedding_path, "wb") as f:
            pickle.dump(embeddings, f)

    def load_index(self):
        if not self.index_path.exists():
            return None
        return faiss.read_index(str(self.index_path))

    def load_metadata(self) -> List[Dict]:
        if not self.metadata_path.exists():
            return []

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)