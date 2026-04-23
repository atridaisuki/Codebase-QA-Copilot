from pathlib import Path

from app.schemas import DocumentRecord

SUPPORTED_EXTENSIONS = {".md": "md", ".txt": "txt"}


class DocumentLoader:
    def load_directory(self, docs_dir: str | Path) -> list[DocumentRecord]:
        root = Path(docs_dir)
        if not root.exists() or not root.is_dir():
            raise FileNotFoundError(f"Document directory not found: {root}")

        documents: list[DocumentRecord] = []
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue

            extension = path.suffix.lower()
            file_type = SUPPORTED_EXTENSIONS.get(extension)
            if not file_type:
                continue

            content = path.read_text(encoding="utf-8").strip()
            if not content:
                continue

            documents.append(
                DocumentRecord(
                    source=path.as_posix(),
                    content=content,
                    file_type=file_type,
                )
            )

        return documents
