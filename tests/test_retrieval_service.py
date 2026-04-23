from app.schemas import SourceItem
from app.services.retrieval_service import RetrievalService, RetrievedChunk


class DummySettings:
    retrieval_fetch_k = 5
    retrieval_score_threshold = 0.5
    grounded_top_score_threshold = 0.7
    grounded_average_score_threshold = 0.6
    grounded_min_chunks = 1
    max_context_chars = 300
    enable_rerank = False
    rerank_top_n = 2
    rerank_model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    enable_hybrid_search = False
    bm25_weight = 1.0
    vector_weight = 1.0
    rrf_k = 60
    bm25_index_path = "data/bm25_index.pkl"


def make_service() -> RetrievalService:
    service = RetrievalService.__new__(RetrievalService)
    service.settings = DummySettings()
    service.embedding_service = None
    service.vector_store = None
    service.bm25_service = None
    service.reranker = None
    return service


def make_chunk(
    *,
    source: str = "doc.md",
    chunk_index: int = 0,
    content: str = "content",
    score: float = 0.8,
    distance: float | None = 0.2,
    start_offset: int | None = 0,
    end_offset: int | None = 10,
    section: str | None = "Section",
) -> RetrievedChunk:
    return RetrievedChunk(
        source=source,
        file_type="md",
        chunk_index=chunk_index,
        content=content,
        score=score,
        distance=distance,
        start_offset=start_offset,
        end_offset=end_offset,
        title=None,
        section=section,
    )


def test_filter_by_score_removes_low_quality_hits() -> None:
    service = make_service()
    chunks = [make_chunk(score=0.82), make_chunk(chunk_index=1, score=0.42)]

    filtered = service._filter_by_score(chunks)

    assert [chunk.chunk_index for chunk in filtered] == [0]


def test_merge_adjacent_chunks_combines_same_source_neighbors() -> None:
    service = make_service()
    chunks = [
        make_chunk(chunk_index=0, content="alpha", start_offset=0, end_offset=5),
        make_chunk(chunk_index=1, content="beta", start_offset=6, end_offset=10),
        make_chunk(source="other.md", chunk_index=0, content="gamma", start_offset=0, end_offset=5),
    ]

    merged = service._merge_adjacent_chunks(chunks)

    assert len(merged) == 2
    assert merged[0].content == "alpha\n\nbeta"
    assert merged[0].chunk_index == 0
    assert merged[0].end_offset == 10


def test_apply_context_budget_trims_to_available_budget() -> None:
    service = make_service()
    service.settings.max_context_chars = 150
    chunks = [
        make_chunk(content="x" * 100, start_offset=0, end_offset=100),
        make_chunk(chunk_index=1, content="y" * 100, start_offset=101, end_offset=201),
    ]

    selected = service._apply_context_budget(chunks)

    assert len(selected) == 1
    assert len(selected[0].content) <= 30


def test_has_sufficient_evidence_uses_scores_not_token_overlap() -> None:
    service = make_service()
    strong_sources = [
        SourceItem(source="doc.md", file_type="md", chunk_index=0, snippet="alpha", score=0.82, distance=0.18)
    ]
    weak_sources = [
        SourceItem(source="doc.md", file_type="md", chunk_index=0, snippet="alpha", score=0.45, distance=0.55)
    ]

    assert service.has_sufficient_evidence("同义问题", strong_sources) is True
    assert service.has_sufficient_evidence("token overlap but irrelevant", weak_sources) is False


def test_retrieve_builds_scored_sources_and_context(monkeypatch) -> None:
    service = make_service()

    class DummyEmbeddingService:
        def embed_query(self, text: str):
            assert text == "Where is the API?"
            return [0.1, 0.2]

    class DummyVectorStore:
        def query(self, query_embedding, top_k: int):
            assert query_embedding == [0.1, 0.2]
            assert top_k == 5
            return {
                "documents": [["Alpha content", "Ignored low score"]],
                "metadatas": [
                    [
                        {
                            "source": "doc.md",
                            "file_type": "md",
                            "chunk_index": 0,
                            "start_offset": 0,
                            "end_offset": 13,
                            "section": "API",
                        },
                        {
                            "source": "doc.md",
                            "file_type": "md",
                            "chunk_index": 1,
                            "start_offset": 14,
                            "end_offset": 31,
                            "section": "Noise",
                        },
                    ]
                ],
                "distances": [[0.1, 0.7]],
            }

    service.embedding_service = DummyEmbeddingService()
    service.vector_store = DummyVectorStore()

    context, sources = service.retrieve("Where is the API?", top_k=2)

    assert "score=0.900" in context
    assert len(sources) == 1
    assert sources[0].source == "doc.md"
    assert sources[0].score == 0.9
    assert sources[0].section == "API"


def test_rrf_merge_combines_two_ranked_lists() -> None:
    service = make_service()
    service.settings.rrf_k = 60
    service.settings.vector_weight = 1.0
    service.settings.bm25_weight = 1.0

    vector_chunks = [
        make_chunk(source="a.md", chunk_index=0, content="alpha", score=0.9),
        make_chunk(source="b.md", chunk_index=0, content="beta", score=0.8),
    ]
    bm25_chunks = [
        make_chunk(source="b.md", chunk_index=0, content="beta", score=0.0),
        make_chunk(source="c.md", chunk_index=0, content="gamma", score=0.0),
    ]

    merged = service._rrf_merge(vector_chunks, bm25_chunks)

    sources = [c.source for c in merged]
    # b.md appears in both lists so should rank highest
    assert sources[0] == "b.md"
    assert len(merged) == 3


def test_hybrid_search_enabled_calls_bm25(monkeypatch) -> None:
    service = make_service()
    service.settings.enable_hybrid_search = True
    service.settings.retrieval_score_threshold = 0.0  # accept all for this test

    class DummyEmbeddingService:
        def embed_query(self, text: str):
            return [0.1]

    class DummyVectorStore:
        def query(self, query_embedding, top_k: int):
            return {
                "documents": [["vector doc"]],
                "metadatas": [[{"source": "v.md", "file_type": "md", "chunk_index": 0,
                                "start_offset": 0, "end_offset": 10}]],
                "distances": [[0.1]],
            }

    class DummyBM25Service:
        def search(self, query, top_k):
            from app.services.bm25_service import BM25Result
            return [BM25Result(
                chunk_id="bm25_1", content="bm25 doc", score=2.5,
                metadata={"source": "b.md", "file_type": "md", "chunk_index": 0,
                           "start_offset": 0, "end_offset": 8},
            )]

    service.embedding_service = DummyEmbeddingService()
    service.vector_store = DummyVectorStore()
    service.bm25_service = DummyBM25Service()

    context, sources = service.retrieve("test query", top_k=3)

    source_names = [s.source for s in sources]
    assert "v.md" in source_names
    assert "b.md" in source_names


def test_apply_rerank_delegates_to_reranker() -> None:
    service = make_service()
    chunks = [
        make_chunk(source="a.md", chunk_index=0, score=0.8),
        make_chunk(source="b.md", chunk_index=0, score=0.9),
    ]

    call_log: list[dict] = []

    class FakeReranker:
        def rerank(self, query, chunks, top_n):
            call_log.append({"query": query, "chunks": chunks, "top_n": top_n})
            return list(reversed(chunks))[:top_n]

    service.reranker = FakeReranker()

    result = service._apply_rerank(chunks, "my question")

    assert len(call_log) == 1
    assert call_log[0]["query"] == "my question"
    assert call_log[0]["top_n"] == service.settings.rerank_top_n
    assert result[0].source == "b.md"


def test_apply_rerank_passthrough_when_no_reranker() -> None:
    service = make_service()
    service.reranker = None
    chunks = [
        make_chunk(source="a.md", chunk_index=0, score=0.8),
        make_chunk(source="b.md", chunk_index=0, score=0.9),
    ]

    result = service._apply_rerank(chunks, "question")

    assert result is chunks
