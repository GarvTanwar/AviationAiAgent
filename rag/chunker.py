from pathlib import Path
from typing import List, Dict
from pypdf import PdfReader


class TextChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 80) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, source_name: str) -> List[Dict]:
        text = text.strip()
        if not text:
            return []

        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "source": source_name,
                        "text": chunk_text,
                    }
                )

            start += self.chunk_size - self.overlap
            chunk_id += 1

        return chunks

    def chunk_file(self, file_path: Path) -> List[Dict]:
        text = file_path.read_text(encoding="utf-8")
        return self.chunk_text(text, file_path.name)

    def extract_text_from_pdf(self, file_path: Path) -> str:
        reader = PdfReader(str(file_path))
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        return "\n".join(text_parts)

    def chunk_pdf(self, file_path: Path) -> List[Dict]:
        text = self.extract_text_from_pdf(file_path)
        return self.chunk_text(text, file_path.name)

    def chunk_directory(self, directory: Path) -> List[Dict]:
        all_chunks = []

        for file_path in directory.glob("*.txt"):
            all_chunks.extend(self.chunk_file(file_path))

        for file_path in directory.glob("*.pdf"):
            all_chunks.extend(self.chunk_pdf(file_path))

        return all_chunks