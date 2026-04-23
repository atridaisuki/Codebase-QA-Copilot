import numpy as np

from app.services.reranker_service import RerankerService
from app.services.retrieval_service import RetrievedChunk


def _make_chunk(content: str, score: float = 0.0, chunk_index: int = 0) -> RetrievedChunk:
    return RetrievedChunk(
        source="doc.md",
        file_type="md",
        chunk_index=chunk_index,
        content=content,
        score=score,
        distance=None,
        start_offset=0,
        end_offset=len(content),
        title=None,
        section=None,
    )


class FakeCrossEncoder:
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name

    def predict(self, pairs):
        # Return descending scores based on pair index reversed,
        # so last pair gets highest score
        n = len(pairs)
        return np.array([float(i) for i in range(n)])


def _make_service(monkeypatch, fake_scores=None) -> RerankerService:
    """Build a RerankerService with a mocked CrossEncoder."""

    class MockCrossEncoder:
        def __init__(self, model_name, **kwargs):
            self.model_name = model_name

        def predict(self, pairs):
            if fake_scores is not None:
                return np.array(fake_scores)
            n = len(pairs)
            return np.array([float(i) for i in range(n)])

    monkeypatch.setattr("app.services.reranker_service.CrossEncoder", MockCrossEncoder)
    monkeypatch.setattr(
        "app.services.reranker_service.get_settings",
        lambda: type("S", (), {"rerank_model_name": "mock-model"})(),
    )
    return RerankerService()


def test_rerank_sorts_by_cross_encoder_score(monkeypatch) -> None:
    service = _make_service(monkeypatch, fake_scores=[1.0, 5.0, 3.0])
    chunks = [
        _make_chunk("low", chunk_index=0),
        _make_chunk("high", chunk_index=1),
        _make_chunk("mid", chunk_index=2),
    ]

    result = service.rerank(query="test", chunks=chunks, top_n=3)

    assert [c.chunk_index for c in result] == [1, 2, 0]


def test_rerank_returns_top_n_only(monkeypatch) -> None:
    service = _make_service(monkeypatch, fake_scores=[1.0, 5.0, 3.0])
    chunks = [
        _make_chunk("a", chunk_index=0),
        _make_chunk("b", chunk_index=1),
        _make_chunk("c", chunk_index=2),
    ]

    result = service.rerank(query="test", chunks=chunks, top_n=2)

    assert len(result) == 2
    assert result[0].chunk_index == 1
    assert result[1].chunk_index == 2


def test_rerank_empty_input_returns_empty(monkeypatch) -> None:
    service = _make_service(monkeypatch)

    result = service.rerank(query="test", chunks=[], top_n=3)

    assert result == []


def test_rerank_overwrites_chunk_scores(monkeypatch) -> None:
    service = _make_service(monkeypatch, fake_scores=[7.5, -2.0])
    chunks = [
        _make_chunk("first", score=0.9, chunk_index=0),
        _make_chunk("second", score=0.8, chunk_index=1),
    ]

    result = service.rerank(query="test", chunks=chunks, top_n=2)

    assert result[0].score == 7.5
    assert result[1].score == -2.0
