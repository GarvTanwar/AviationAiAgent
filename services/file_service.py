from pathlib import Path


KNOWLEDGE_BASE_DIR = Path("knowledge_base")
ALLOWED_EXTENSIONS = {".txt", ".pdf"}


def ensure_knowledge_base_dir() -> None:
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(uploaded_file) -> Path:
    ensure_knowledge_base_dir()

    file_name = Path(uploaded_file.name).name
    extension = Path(file_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only .txt and .pdf files are allowed.")

    save_path = KNOWLEDGE_BASE_DIR / file_name

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return save_path