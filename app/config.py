from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Codebase QA Copilot")
    app_env: str = Field(default="development")
    api_prefix: str = Field(default="")
    default_docs_dir: str = Field(default="data/docs")
    chroma_persist_directory: str = Field(default="data/chroma")
    chroma_collection_name: str = Field(default="documents")
    embedding_model_name: str = Field(default="BAAI/bge-base-zh-v1.5")
    chunk_size: int = Field(default=800)
    chunk_overlap: int = Field(default=120)
    default_top_k: int = Field(default=3)
    retrieval_fetch_k: int = Field(default=6)
    retrieval_score_threshold: float = Field(default=0.4)
    grounded_top_score_threshold: float = Field(default=0.65)
    grounded_average_score_threshold: float = Field(default=0.5)
    grounded_min_chunks: int = Field(default=1)
    max_context_chars: int = Field(default=3200)
    enable_rerank: bool = Field(default=True)
    rerank_top_n: int = Field(default=3)
    rerank_model_name: str = Field(default="BAAI/bge-reranker-base")
    enable_hybrid_search: bool = Field(default=True)
    bm25_weight: float = Field(default=1.0)
    vector_weight: float = Field(default=1.0)
    rrf_k: int = Field(default=60)
    bm25_index_path: str = Field(default="data/bm25_index.pkl")
    llm_provider: str = Field(default="anthropic")
    anthropic_api_key: str | None = Field(default=None)
    anthropic_base_url: str | None = Field(default=None)
    anthropic_model: str = Field(default="claude-opus-4-6")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def docs_path(self) -> Path:
        return Path(self.default_docs_dir)

    @property
    def chroma_path(self) -> Path:
        return Path(self.chroma_persist_directory)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
