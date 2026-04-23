from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import torch
from sentence_transformers import CrossEncoder

from app.config import get_settings

if TYPE_CHECKING:
    from app.services.retrieval_service import RetrievedChunk

logger = logging.getLogger(__name__)


class RerankerService:
    def __init__(self) -> None:
        settings = get_settings()
        model_name = settings.rerank_model_name
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("Loading reranker model: %s (device=%s)", model_name, device)
        self.model = CrossEncoder(model_name, device=device)

    def rerank(self, query: str, chunks: list[RetrievedChunk], top_n: int) -> list[RetrievedChunk]:
        if not chunks:
            return []

        pairs = [(query, chunk.content) for chunk in chunks]
        raw_scores = self.model.predict(pairs)

        for chunk, raw in zip(chunks, raw_scores, strict=True):
            chunk.score = self._sigmoid(float(raw))

        ranked = sorted(chunks, key=lambda c: c.score, reverse=True)
        return ranked[:top_n]

    @staticmethod
    def _sigmoid(x: float) -> float:
        import math
        return 1.0 / (1.0 + math.exp(-x))
