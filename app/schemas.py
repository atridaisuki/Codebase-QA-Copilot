from typing import Any, Literal

from pydantic import BaseModel, Field


class DocumentRecord(BaseModel):
    source: str
    content: str
    file_type: Literal["md", "txt"]


class ChunkRecord(BaseModel):
    id: str
    source: str
    file_type: Literal["md", "txt"]
    chunk_index: int
    content: str
    start_offset: int
    end_offset: int
    title: str | None = None
    section: str | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    environment: str


class IngestRequest(BaseModel):
    docs_dir: str | None = None


class IngestResponse(BaseModel):
    files_count: int
    chunks_count: int
    collection_name: str


class ErrorResponse(BaseModel):
    detail: str
    request_id: str


class SourceItem(BaseModel):
    source: str
    file_type: Literal["md", "txt"] | None = None
    chunk_index: int
    snippet: str
    score: float | None = None
    distance: float | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    title: str | None = None
    section: str | None = None


class QARequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=10)


class QAResponse(BaseModel):
    answer: str
    grounded: bool
    sources: list[SourceItem]


# ---------------------------------------------------------------------------
# Agent schemas
# ---------------------------------------------------------------------------


class ChatMessage(BaseModel):
    role: str
    content: str


class ToolStep(BaseModel):
    tool_name: str
    tool_input: dict[str, Any]
    tool_result: str


class AgentRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None


class AgentResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: list[SourceItem]
    tool_steps: list[ToolStep]
