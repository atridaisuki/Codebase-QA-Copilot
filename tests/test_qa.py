from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class EmptyRetrievalService:
    def retrieve(self, question: str, top_k: int):
        return "", []

    def has_sufficient_evidence(self, question: str, sources) -> bool:
        return False


class ReadyRetrievalService:
    def retrieve(self, question: str, top_k: int):
        return (
            "[1] source=data/docs/product.md\nfile_type=md\nchunk_index=0\nscore=0.910\noffsets=0-42\nsection=API\ncontent:\nPOST /qa answers questions.",
            [
                {
                    "source": "data/docs/product.md",
                    "file_type": "md",
                    "chunk_index": 0,
                    "snippet": "POST /qa answers questions.",
                    "score": 0.91,
                    "distance": 0.09,
                    "start_offset": 0,
                    "end_offset": 42,
                    "section": "API",
                    "title": None,
                }
            ],
        )

    def has_sufficient_evidence(self, question: str, sources) -> bool:
        return True


class DefaultTopKRetrievalService:
    def retrieve(self, question: str, top_k: int):
        assert top_k == 3
        return (
            "[1] source=data/docs/product.md\nfile_type=md\nchunk_index=0\nscore=0.910\noffsets=0-42\nsection=API\ncontent:\nPOST /qa answers questions.",
            [
                {
                    "source": "data/docs/product.md",
                    "file_type": "md",
                    "chunk_index": 0,
                    "snippet": "POST /qa answers questions.",
                    "score": 0.91,
                    "distance": 0.09,
                    "start_offset": 0,
                    "end_offset": 42,
                    "section": "API",
                    "title": None,
                }
            ],
        )

    def has_sufficient_evidence(self, question: str, sources) -> bool:
        return True


class WeakEvidenceRetrievalService:
    def retrieve(self, question: str, top_k: int):
        return (
            "[1] source=data/docs/overview.txt\nfile_type=txt\nchunk_index=0\nscore=0.410\noffsets=0-36\nsection=overview\ncontent:\nThis project uses FastAPI and Chroma.",
            [
                {
                    "source": "data/docs/overview.txt",
                    "file_type": "txt",
                    "chunk_index": 0,
                    "snippet": "This project uses FastAPI and Chroma.",
                    "score": 0.41,
                    "distance": 0.59,
                    "start_offset": 0,
                    "end_offset": 36,
                    "section": "overview",
                    "title": None,
                }
            ],
        )

    def has_sufficient_evidence(self, question: str, sources) -> bool:
        return False


class DummyVectorStoreEmpty:
    def count(self) -> int:
        return 0


class DummyVectorStoreReady:
    def count(self) -> int:
        return 5


class DummyLLMService:
    def generate_answer(self, prompt: str, sources=None) -> str:
        assert "Retrieved context" in prompt
        assert "score=0.910" in prompt
        return "The system supports POST /qa for question answering."


def test_qa_returns_error_when_no_indexed_content(monkeypatch) -> None:
    # retrieval service会引入很多测试环境没有的东西，直接替换成一个空的
    # 临时指向另一个类，测试结束后恢复
    monkeypatch.setattr("app.routers.qa.RetrievalService", EmptyRetrievalService)
    monkeypatch.setattr("app.routers.qa.VectorStore", DummyVectorStoreEmpty)

    response = client.post("/qa", json={"question": "What APIs are available?"})

    assert response.status_code == 400
    assert response.headers["X-Request-ID"]
    payload = response.json()
    assert payload["detail"] == "No indexed content found. Please ingest documents first."
    assert payload["request_id"] == response.headers["X-Request-ID"]


def test_qa_returns_insufficient_evidence_answer(monkeypatch) -> None:
    monkeypatch.setattr("app.routers.qa.RetrievalService", WeakEvidenceRetrievalService)
    monkeypatch.setattr("app.routers.qa.LLMService", DummyLLMService)
    monkeypatch.setattr("app.routers.qa.VectorStore", DummyVectorStoreReady)

    response = client.post("/qa", json={"question": "What authentication method is supported?", "top_k": 1})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    payload = response.json()
    assert payload["answer"] == "根据当前文档无法确定。"
    assert payload["grounded"] is False
    assert payload["sources"] == [
        {
            "source": "data/docs/overview.txt",
            "file_type": "txt",
            "chunk_index": 0,
            "snippet": "This project uses FastAPI and Chroma.",
            "score": 0.41,
            "distance": 0.59,
            "start_offset": 0,
            "end_offset": 36,
            "title": None,
            "section": "overview",
        }
    ]


def test_qa_returns_answer_and_sources(monkeypatch) -> None:
    monkeypatch.setattr("app.routers.qa.RetrievalService", ReadyRetrievalService)
    monkeypatch.setattr("app.routers.qa.LLMService", DummyLLMService)
    monkeypatch.setattr("app.routers.qa.VectorStore", DummyVectorStoreReady)

    response = client.post("/qa", json={"question": "What APIs are available?", "top_k": 1})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    payload = response.json()
    assert payload["answer"] == "The system supports POST /qa for question answering."
    assert payload["grounded"] is True
    assert payload["sources"] == [
        {
            "source": "data/docs/product.md",
            "file_type": "md",
            "chunk_index": 0,
            "snippet": "POST /qa answers questions.",
            "score": 0.91,
            "distance": 0.09,
            "start_offset": 0,
            "end_offset": 42,
            "title": None,
            "section": "API",
        }
    ]


def test_qa_uses_default_top_k_when_not_provided(monkeypatch) -> None:
    monkeypatch.setattr("app.routers.qa.RetrievalService", DefaultTopKRetrievalService)
    monkeypatch.setattr("app.routers.qa.LLMService", DummyLLMService)
    monkeypatch.setattr("app.routers.qa.VectorStore", DummyVectorStoreReady)

    response = client.post("/qa", json={"question": "What APIs are available?"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert response.json()["grounded"] is True


def test_qa_returns_validation_error_shape() -> None:
    response = client.post("/qa", json={"question": ""})

    assert response.status_code == 422
    assert response.headers["X-Request-ID"]
    payload = response.json()
    assert payload["detail"] == "Request validation failed."
    assert payload["request_id"] == response.headers["X-Request-ID"]


def test_llm_service_omits_thinking_and_effort_for_custom_base_url(monkeypatch) -> None:
    calls = []

    class DummyMessages:
        def create(self, **kwargs):
            calls.append(kwargs)
            return type(
                "Response", (), {"content": [type("TextBlock", (), {"type": "text", "text": "Proxy answer"})()]}
            )()

    class DummyAnthropicClient:
        def __init__(self, **kwargs):
            self.init_kwargs = kwargs
            self.messages = DummyMessages()

    monkeypatch.setattr(
        "app.services.llm_service.get_settings",
        lambda: type(
            "Settings",
            (),
            {
                "anthropic_api_key": "test-key",
                "anthropic_base_url": "https://right.codes/o2a",
                "anthropic_model": "claude-opus-4-6",
            },
        )(),
    )
    monkeypatch.setattr("app.services.llm_service.anthropic.Anthropic", DummyAnthropicClient)

    from app.services.llm_service import LLMService

    answer = LLMService().generate_answer(prompt="hello")

    assert answer == "Proxy answer"
    assert calls == [
        {
            "model": "claude-opus-4-6",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": "hello"}],
        }
    ]


def test_llm_service_returns_fallback_answer_without_api_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.llm_service.get_settings",
        lambda: type(
            "Settings",
            (),
            {
                "anthropic_api_key": None,
                "anthropic_base_url": None,
                "anthropic_model": "claude-opus-4-6",
            },
        )(),
    )

    from app.services.llm_service import LLMService

    service = LLMService()
    answer = service.generate_answer(
        prompt="hello",
        sources=[
            {
                "source": "data/docs/product.md",
                "chunk_index": 2,
                "snippet": "Fallback snippet.",
            }
        ],
    )

    assert (
        answer
        == "Anthropic API key is not configured. Grounded excerpt from data/docs/product.md (chunk 2): Fallback snippet."
    )
