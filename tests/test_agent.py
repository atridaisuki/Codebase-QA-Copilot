import json

from fastapi.testclient import TestClient

from app.core.conversation_store import conversation_store
from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------


class DummyVectorStoreReady:
    def count(self) -> int:
        return 5

    def get_all_metadata(self) -> list[dict]:
        return [
            {"source": "data/docs/python.md", "file_type": "md", "chunk_index": 0, "section": "GIL"},
            {"source": "data/docs/python.md", "file_type": "md", "chunk_index": 1, "section": "Concurrency"},
            {"source": "data/docs/docker.md", "file_type": "md", "chunk_index": 0, "section": "Overview"},
        ]


class StubRetrievalService:
    """Retrieval service that returns canned results for knowledge_search."""

    def retrieve(self, question: str, top_k: int):
        return (
            f"[1] source=data/docs/python.md\nscore=0.910\ncontent:\nPython GIL info for: {question}",
            [
                {
                    "source": "data/docs/python.md",
                    "file_type": "md",
                    "chunk_index": 0,
                    "snippet": f"Python GIL info for: {question}",
                    "score": 0.91,
                    "distance": 0.09,
                    "start_offset": 0,
                    "end_offset": 42,
                    "title": None,
                    "section": "GIL",
                }
            ],
        )

    def has_sufficient_evidence(self, question, sources):
        return True

    def list_sources(self):
        return ["data/docs/python.md", "data/docs/docker.md"]

    def get_sections(self, source):
        if source == "data/docs/python.md":
            return [
                {"section": "GIL", "chunk_index": 0},
                {"section": "Concurrency", "chunk_index": 1},
            ]
        return []


# ---------------------------------------------------------------------------
# Helpers to build fake Claude responses
# ---------------------------------------------------------------------------


def _text_block(text: str):
    return type("TextBlock", (), {"type": "text", "text": text})()


def _tool_use_block(tool_id: str, name: str, input_data: dict):
    return type("ToolUseBlock", (), {"type": "tool_use", "id": tool_id, "name": name, "input": input_data})()


def _make_response(content, stop_reason="end_turn"):
    return type("Response", (), {"content": content, "stop_reason": stop_reason})()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_agent_direct_answer(monkeypatch) -> None:
    """When Claude answers directly without tools, no tool_steps should appear."""
    call_count = 0

    class FakeClient:
        class messages:
            @staticmethod
            def create(**kwargs):
                nonlocal call_count
                call_count += 1
                return _make_response([_text_block("你好！有什么可以帮你的？")])

    monkeypatch.setattr("app.services.agent_service.RetrievalService", StubRetrievalService)
    monkeypatch.setattr("app.services.agent_service.anthropic.Anthropic", lambda **kw: FakeClient())
    monkeypatch.setattr(
        "app.services.agent_service.get_settings",
        lambda: type("S", (), {
            "anthropic_api_key": "test-key",
            "anthropic_base_url": None,
            "anthropic_model": "claude-opus-4-6",
            "agent_max_iterations": 5,
            "agent_max_tokens": 2048,
            "enable_hybrid_search": False,
            "enable_rerank": False,
        })(),
    )

    response = client.post("/agent/chat", json={"message": "你好"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "你好！有什么可以帮你的？"
    assert payload["tool_steps"] == []
    assert payload["sources"] == []
    assert payload["conversation_id"]
    assert call_count == 1


def _make_settings():
    return type("S", (), {
        "anthropic_api_key": "test-key",
        "anthropic_base_url": None,
        "anthropic_model": "claude-opus-4-6",
        "agent_max_iterations": 5,
        "agent_max_tokens": 2048,
        "enable_hybrid_search": False,
        "enable_rerank": False,
    })()


def test_agent_single_search(monkeypatch) -> None:
    """Claude calls knowledge_search once, then gives final answer."""
    call_count = 0

    class FakeClient:
        class messages:
            @staticmethod
            def create(**kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return _make_response(
                        [_tool_use_block("tu_1", "knowledge_search", {"query": "GIL"})],
                        stop_reason="tool_use",
                    )
                return _make_response([_text_block("GIL是Python的全局解释器锁。")])

    monkeypatch.setattr("app.services.agent_service.RetrievalService", StubRetrievalService)
    monkeypatch.setattr("app.services.agent_service.anthropic.Anthropic", lambda **kw: FakeClient())
    monkeypatch.setattr("app.services.agent_service.get_settings", _make_settings)

    response = client.post("/agent/chat", json={"message": "什么是GIL？"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "GIL是Python的全局解释器锁。"
    assert len(payload["tool_steps"]) == 1
    assert payload["tool_steps"][0]["tool_name"] == "knowledge_search"
    assert len(payload["sources"]) == 1
    assert call_count == 2


def test_agent_multi_step_search(monkeypatch) -> None:
    """Claude calls knowledge_search twice with different queries."""
    call_count = 0

    class FakeClient:
        class messages:
            @staticmethod
            def create(**kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return _make_response(
                        [_tool_use_block("tu_1", "knowledge_search", {"query": "GIL"})],
                        stop_reason="tool_use",
                    )
                if call_count == 2:
                    return _make_response(
                        [_tool_use_block("tu_2", "knowledge_search", {"query": "Redis单线程"})],
                        stop_reason="tool_use",
                    )
                return _make_response([_text_block("GIL和Redis单线程模型的比较...")])

    monkeypatch.setattr("app.services.agent_service.RetrievalService", StubRetrievalService)
    monkeypatch.setattr("app.services.agent_service.anthropic.Anthropic", lambda **kw: FakeClient())
    monkeypatch.setattr("app.services.agent_service.get_settings", _make_settings)

    response = client.post("/agent/chat", json={"message": "比较GIL和Redis单线程模型"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["tool_steps"]) == 2
    assert payload["tool_steps"][0]["tool_input"]["query"] == "GIL"
    assert payload["tool_steps"][1]["tool_input"]["query"] == "Redis单线程"
    assert call_count == 3


def test_agent_max_iterations(monkeypatch) -> None:
    """Agent stops after max_iterations even if Claude keeps requesting tools."""

    class FakeClient:
        class messages:
            @staticmethod
            def create(**kwargs):
                return _make_response(
                    [
                        _text_block("让我搜索一下..."),
                        _tool_use_block("tu_x", "knowledge_search", {"query": "loop"}),
                    ],
                    stop_reason="tool_use",
                )

    def settings_2_iter():
        return type("S", (), {
            "anthropic_api_key": "test-key",
            "anthropic_base_url": None,
            "anthropic_model": "claude-opus-4-6",
            "agent_max_iterations": 2,
            "agent_max_tokens": 2048,
            "enable_hybrid_search": False,
            "enable_rerank": False,
        })()

    monkeypatch.setattr("app.services.agent_service.RetrievalService", StubRetrievalService)
    monkeypatch.setattr("app.services.agent_service.anthropic.Anthropic", lambda **kw: FakeClient())
    monkeypatch.setattr("app.services.agent_service.get_settings", settings_2_iter)

    response = client.post("/agent/chat", json={"message": "无限循环测试"})

    assert response.status_code == 200
    payload = response.json()
    # Should have exactly 2 tool steps (max_iterations=2)
    assert len(payload["tool_steps"]) == 2
    # Answer is extracted from the last response's text block
    assert "让我搜索一下" in payload["answer"]


def test_agent_sse_stream(monkeypatch) -> None:
    """SSE endpoint returns events in correct order: tool_call → tool_result → text → done."""
    call_count = 0

    class FakeClient:
        class messages:
            @staticmethod
            def create(**kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return _make_response(
                        [_tool_use_block("tu_1", "knowledge_search", {"query": "GIL"})],
                        stop_reason="tool_use",
                    )
                return _make_response([_text_block("GIL是全局解释器锁。")])

    monkeypatch.setattr("app.services.agent_service.RetrievalService", StubRetrievalService)
    monkeypatch.setattr("app.services.agent_service.anthropic.Anthropic", lambda **kw: FakeClient())
    monkeypatch.setattr("app.services.agent_service.get_settings", _make_settings)

    response = client.post(
        "/agent/chat/stream",
        json={"message": "什么是GIL？"},
        headers={"Accept": "text/event-stream"},
    )

    assert response.status_code == 200
    # Parse SSE events
    events = []
    for line in response.text.strip().split("\n"):
        line = line.strip()
        if line.startswith("event:"):
            events.append({"event": line.split(":", 1)[1].strip()})
        elif line.startswith("data:") and events:
            events[-1]["data"] = line.split(":", 1)[1].strip()

    event_types = [e["event"] for e in events]
    assert "tool_call" in event_types
    assert "tool_result" in event_types
    assert "text" in event_types
    assert event_types[-1] == "done"


def test_agent_multi_turn(monkeypatch) -> None:
    """Multi-turn conversation uses conversation_id to maintain context."""
    call_count = 0

    class FakeClient:
        class messages:
            @staticmethod
            def create(**kwargs):
                nonlocal call_count
                call_count += 1
                msgs = kwargs.get("messages", [])
                if call_count == 1:
                    return _make_response([_text_block("GIL是全局解释器锁。")])
                # Second call should have conversation history
                assert len(msgs) >= 3  # user1 + assistant1 + user2
                return _make_response([_text_block("GIL的缺点是限制多线程并行。")])

    monkeypatch.setattr("app.services.agent_service.RetrievalService", StubRetrievalService)
    monkeypatch.setattr("app.services.agent_service.anthropic.Anthropic", lambda **kw: FakeClient())
    monkeypatch.setattr("app.services.agent_service.get_settings", _make_settings)

    # First turn
    r1 = client.post("/agent/chat", json={"message": "什么是GIL？"})
    assert r1.status_code == 200
    cid = r1.json()["conversation_id"]
    assert cid

    # Second turn with same conversation_id
    r2 = client.post("/agent/chat", json={"message": "它有什么缺点？", "conversation_id": cid})
    assert r2.status_code == 200
    assert r2.json()["conversation_id"] == cid
    assert r2.json()["answer"] == "GIL的缺点是限制多线程并行。"
    assert call_count == 2


def test_agent_list_documents_tool(monkeypatch) -> None:
    """Agent can use list_documents tool."""
    call_count = 0

    class FakeClient:
        class messages:
            @staticmethod
            def create(**kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return _make_response(
                        [_tool_use_block("tu_1", "list_documents", {})],
                        stop_reason="tool_use",
                    )
                return _make_response([_text_block("知识库中有python.md和docker.md两个文档。")])

    monkeypatch.setattr("app.services.agent_service.RetrievalService", StubRetrievalService)
    monkeypatch.setattr("app.services.agent_service.anthropic.Anthropic", lambda **kw: FakeClient())
    monkeypatch.setattr("app.services.agent_service.get_settings", _make_settings)

    response = client.post("/agent/chat", json={"message": "知识库里有什么文档？"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["tool_steps"]) == 1
    assert payload["tool_steps"][0]["tool_name"] == "list_documents"
    assert "python.md" in payload["tool_steps"][0]["tool_result"]
