from __future__ import annotations

from typing import TYPE_CHECKING, Any

from chromadb import PersistentClient

from app.config import get_settings
from app.schemas import ChunkRecord

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection


class VectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        settings.chroma_path.mkdir(parents=True, exist_ok=True)
        self.collection_name = settings.chroma_collection_name
        self.client = PersistentClient(path=str(settings.chroma_path))
        self.collection: Collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, chunks: list[ChunkRecord], embeddings: list[list[float]]) -> None:
        if not chunks:
            return

        self.collection.upsert(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.content for chunk in chunks],
            embeddings=embeddings,  # type: ignore[arg-type]
            metadatas=[
                {
                    "source": chunk.source,
                    "file_type": chunk.file_type,
                    "chunk_index": chunk.chunk_index,
                    "start_offset": chunk.start_offset,
                    "end_offset": chunk.end_offset,
                    "title": chunk.title,
                    "section": chunk.section,
                }
                for chunk in chunks
            ],
        )

    def query(self, query_embedding: list[float], top_k: int) -> dict[str, Any]:
        result: dict[str, Any] = self.collection.query(  # type: ignore[assignment]
            query_embeddings=[query_embedding],  # type: ignore[arg-type]
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        return result

    def count(self) -> int:
        return self.collection.count()

    def get_all_metadata(self) -> list[dict[str, Any]]:
        result = self.collection.get(include=["metadatas"])
        return list(result.get("metadatas") or [])
