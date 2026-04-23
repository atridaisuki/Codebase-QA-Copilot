from pathlib import Path

from app.services.document_loader import DocumentLoader


def test_loader_reads_supported_files(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "a.md").write_text("# Hello", encoding="utf-8")
    (docs_dir / "b.txt").write_text("world", encoding="utf-8")
    (docs_dir / "ignore.json").write_text("{}", encoding="utf-8")
    (docs_dir / "empty.txt").write_text("   ", encoding="utf-8")

    loader = DocumentLoader()
    documents = loader.load_directory(docs_dir)

    assert len(documents) == 2
    assert {doc.file_type for doc in documents} == {"md", "txt"}
