from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class DummyLoader:
    def load_directory(self, docs_dir: str):
        return [object(), object()]


class EmptyLoader:
    def load_directory(self, docs_dir: str):
        return []


class MissingLoader:
    def load_directory(self, docs_dir: str):
        raise FileNotFoundError(f"Document directory not found: {docs_dir}")


class DummySplitter:
    def split_documents(self, documents):
        return [
            type("Chunk", (), {"content": "alpha", "id": "1", "source": "a.md", "file_type": "md", "chunk_index": 0,
                               "start_offset": 0, "end_offset": 5, "title": None, "section": None})(),
            type("Chunk", (), {"content": "beta", "id": "2", "source": "b.txt", "file_type": "txt", "chunk_index": 1,
                               "start_offset": 0, "end_offset": 4, "title": None, "section": None})(),
        ]


class DummyEmbeddingService:
    def embed_documents(self, texts):
        assert texts == ["alpha", "beta"]
        return [[0.1, 0.2], [0.3, 0.4]]


class DummyVectorStore:
    def __init__(self):
        self.collection_name = "documents"

    def upsert_chunks(self, chunks, embeddings):
        assert len(chunks) == 2
        assert len(embeddings) == 2


def test_ingest_returns_counts(monkeypatch) -> None:
    monkeypatch.setattr("app.routers.ingest.DocumentLoader", DummyLoader)
    monkeypatch.setattr("app.routers.ingest.TextSplitter", DummySplitter)
    monkeypatch.setattr("app.routers.ingest.EmbeddingService", DummyEmbeddingService)
    monkeypatch.setattr("app.routers.ingest.VectorStore", DummyVectorStore)

    response = client.post("/ingest", json={"docs_dir": "data/docs"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert response.json() == {
        "files_count": 2,
        "chunks_count": 2,
        "collection_name": "documents",
    }


def test_ingest_returns_error_when_no_supported_documents_found(monkeypatch) -> None:
    monkeypatch.setattr("app.routers.ingest.DocumentLoader", EmptyLoader)
    monkeypatch.setattr("app.routers.ingest.TextSplitter", DummySplitter)
    monkeypatch.setattr("app.routers.ingest.EmbeddingService", DummyEmbeddingService)
    monkeypatch.setattr("app.routers.ingest.VectorStore", DummyVectorStore)

    response = client.post("/ingest", json={"docs_dir": "data/empty"})

    assert response.status_code == 400
    assert response.headers["X-Request-ID"]
    payload = response.json()
    assert payload["detail"] == "No supported documents found to ingest."
    assert payload["request_id"] == response.headers["X-Request-ID"]


def test_ingest_returns_not_found_for_missing_directory(monkeypatch) -> None:
    monkeypatch.setattr("app.routers.ingest.DocumentLoader", MissingLoader)
    monkeypatch.setattr("app.routers.ingest.TextSplitter", DummySplitter)
    monkeypatch.setattr("app.routers.ingest.EmbeddingService", DummyEmbeddingService)
    monkeypatch.setattr("app.routers.ingest.VectorStore", DummyVectorStore)

    response = client.post("/ingest", json={"docs_dir": "data/missing"})

    assert response.status_code == 404
    assert response.headers["X-Request-ID"]
    payload = response.json()
    assert payload["detail"] == "Document directory not found: data/missing"
    assert payload["request_id"] == response.headers["X-Request-ID"]
