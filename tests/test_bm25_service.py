import pickle
from pathlib import Path

from app.schemas import ChunkRecord
from app.services.bm25_service import BM25Service, _tokenize


def _make_chunk(id: str, content: str, index: int = 0) -> ChunkRecord:
    return ChunkRecord(
        id=id, source="test.md", file_type="md", chunk_index=index,
        content=content, start_offset=0, end_offset=len(content),
    )


class DummySettings:
    bm25_index_path = "data/_test_bm25.pkl"


def _make_service(tmp_path: Path) -> BM25Service:
    service = BM25Service.__new__(BM25Service)
    service.settings = DummySettings()
    service.settings.bm25_index_path = str(tmp_path / "bm25.pkl")
    service._bm25 = None
    service._chunks = []
    return service


def test_index_and_search(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    chunks = [
        _make_chunk("c1", "Python is a programming language", 0),
        _make_chunk("c2", "Java is also a programming language", 1),
        _make_chunk("c3", "The weather is sunny today", 2),
    ]
    service.index(chunks)

    results = service.search("Python programming", top_k=2)
    assert len(results) >= 1
    assert results[0].chunk_id == "c1"
    assert results[0].score > 0


def test_search_empty_corpus(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    service.index([])
    results = service.search("anything", top_k=5)
    assert results == []


def test_persist_and_load(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    chunks = [
        _make_chunk("c1", "hello world programming", 0),
        _make_chunk("c2", "goodbye universe science", 1),
        _make_chunk("c3", "another document about math", 2),
    ]
    service.index(chunks)

    # Load into a fresh service
    service2 = _make_service(tmp_path)
    service2.load_index()
    results = service2.search("hello", top_k=1)
    assert len(results) == 1
    assert results[0].chunk_id == "c1"


def test_load_index_missing_file(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    service.load_index()  # should not raise
    assert service._bm25 is None


def test_tokenize_english() -> None:
    tokens = _tokenize("Hello World")
    assert tokens == ["hello", "world"]


def test_tokenize_chinese() -> None:
    tokens = _tokenize("今天天气不错")
    assert len(tokens) > 1  # jieba should split into multiple tokens
