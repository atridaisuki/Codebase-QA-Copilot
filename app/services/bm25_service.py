from __future__ import annotations

import pickle
import re
from dataclasses import dataclass
from pathlib import Path

from rank_bm25 import BM25Okapi

from app.config import get_settings
from app.schemas import ChunkRecord


@dataclass(slots=True)
class BM25Result:
    chunk_id: str
    content: str
    score: float
    metadata: dict


_HAS_CHINESE = re.compile(r"[\u4e00-\u9fff]")


def _tokenize(text: str) -> list[str]:
    """Tokenize text: jieba for Chinese, whitespace split for English."""
    if _HAS_CHINESE.search(text):
        import jieba
        return list(jieba.cut(text))
    return text.lower().split()


class BM25Service:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._bm25: BM25Okapi | None = None
        self._chunks: list[dict] = []

    def index(self, chunks: list[ChunkRecord]) -> None:
        """Build BM25 index from chunks and persist to disk."""
        self._chunks = [
            {"id": c.id, "content": c.content, "source": c.source,
             "file_type": c.file_type, "chunk_index": c.chunk_index,
             "start_offset": c.start_offset, "end_offset": c.end_offset,
             "title": c.title, "section": c.section}
            for c in chunks
        ]
        corpus = [_tokenize(c.content) for c in chunks]
        if not corpus:
            self._bm25 = None
            return

        self._bm25 = BM25Okapi(corpus)
        self._persist()

    def search(self, query: str, top_k: int = 5) -> list[BM25Result]:
        """Search the BM25 index and return top_k results."""
        if self._bm25 is None or not self._chunks:
            return []

        tokens = _tokenize(query)
        scores = self._bm25.get_scores(tokens)

        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        results: list[BM25Result] = []
        for idx, score in ranked:
            if score <= 0:
                continue
            chunk = self._chunks[idx]
            results.append(BM25Result(
                chunk_id=chunk["id"],
                content=chunk["content"],
                score=float(score),
                metadata=chunk,
            ))
        return results

    def load_index(self) -> None:
        """Load a previously persisted BM25 index from disk."""
        index_path = Path(self.settings.bm25_index_path)
        if not index_path.exists():
            return
        with open(index_path, "rb") as f:
            data = pickle.load(f)  # noqa: S301
        self._bm25 = data["bm25"]
        self._chunks = data["chunks"]

    def _persist(self) -> None:
        index_path = Path(self.settings.bm25_index_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(index_path, "wb") as f:
            pickle.dump({"bm25": self._bm25, "chunks": self._chunks}, f)
