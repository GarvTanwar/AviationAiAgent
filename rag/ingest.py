from pathlib import Path

from rag.chunker import TextChunker
from rag.embedder import EmbeddingService
from rag.vector_store import FAISSVectorStore


def ingest_knowledge_base(
    knowledge_dir: str = "knowledge_base",
    store_dir: str = "rag_store",
) -> int:
    knowledge_path = Path(knowledge_dir)

    if not knowledge_path.exists():
        raise FileNotFoundError(f"Knowledge base folder not found: {knowledge_dir}")

    chunker = TextChunker()
    embedder = EmbeddingService()
    vector_store = FAISSVectorStore(store_dir=store_dir)

    chunks = chunker.chunk_directory(knowledge_path)

    if not chunks:
        raise ValueError("No knowledge base text or PDF files found to ingest.")

    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedder.embed_texts(texts)

    vector_store.save(embeddings, chunks)

    print(f"Ingestion complete. Stored {len(chunks)} chunks in {store_dir}.")
    return len(chunks)