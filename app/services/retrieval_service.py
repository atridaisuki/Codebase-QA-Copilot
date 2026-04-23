from dataclasses import dataclass

from app.config import get_settings
from app.schemas import SourceItem
from app.services.bm25_service import BM25Service
from app.services.embedding_service import EmbeddingService
from app.services.reranker_service import RerankerService
from app.services.vector_store import VectorStore


@dataclass(slots=True)
class RetrievedChunk:
    source: str
    file_type: str | None
    chunk_index: int
    content: str
    score: float
    distance: float | None
    start_offset: int | None
    end_offset: int | None
    title: str | None
    section: str | None


class RetrievalService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.bm25_service = BM25Service()
        self.bm25_service.load_index()
        self.reranker = RerankerService() if self.settings.enable_rerank else None

    def retrieve(self, question: str, top_k: int) -> tuple[str, list[SourceItem]]:
        fetch_k = max(top_k, self.settings.retrieval_fetch_k)

        #向量化问题
        query_embedding = self.embedding_service.embed_query(question)
        #从向量库查找（召回）
        results = self.vector_store.query(query_embedding=query_embedding, top_k=fetch_k)

        #检索向量
        retrieved_chunks = self._parse_results(results)

        #rrf融合
        if self.settings.enable_hybrid_search:
            #bm25召回
            bm25_results = self.bm25_service.search(question, top_k=fetch_k)
            bm25_chunks = [
                RetrievedChunk(
                    source=str(r.metadata.get("source", "unknown")),
                    file_type=r.metadata.get("file_type"),
                    chunk_index=int(r.metadata.get("chunk_index", 0)),
                    content=r.content,
                    score=0.0,  # placeholder, RRF will assign final score
                    distance=None,
                    start_offset=self._safe_int(r.metadata.get("start_offset")),
                    end_offset=self._safe_int(r.metadata.get("end_offset")),
                    title=self._safe_str(r.metadata.get("title")),
                    section=self._safe_str(r.metadata.get("section")),
                )
                for r in bm25_results
            ]
            #融合
            retrieved_chunks = self._rrf_merge(retrieved_chunks, bm25_chunks)

        #筛选，分数过滤（hybrid 模式下 RRF 分数量纲不同，跳过阈值过滤）
        if not self.settings.enable_hybrid_search:
            retrieved_chunks = self._filter_by_score(retrieved_chunks)
        #rerank重排序（保留至少 top_k 条，避免 rerank_top_n 过小截断候选）
        rerank_n = max(self.settings.rerank_top_n, top_k)
        ranked_chunks = self._apply_rerank(retrieved_chunks, question, rerank_n=rerank_n)
        #精选
        prompt_chunks = self._select_prompt_chunks(ranked_chunks, top_k=top_k)

        #格式化，并喂给llm
        context = self._build_context(prompt_chunks)
        #转成api返回的source item
        sources = [self._to_source_item(chunk) for chunk in ranked_chunks[:top_k]]
        return context, sources

    def has_sufficient_evidence(self, _question: str, sources: list[SourceItem]) -> bool:
        if not sources:
            return False

        scored_sources = [source for source in sources if source.score is not None]
        if not scored_sources:
            return False

        top_score = max(source.score for source in scored_sources if source.score is not None)
        average_score = sum(source.score for source in scored_sources if source.score is not None) / len(scored_sources)

        if top_score < self.settings.grounded_top_score_threshold:
            return False
        if average_score < self.settings.grounded_average_score_threshold:
            return False

        valid_chunks = [
            source for source in scored_sources if (source.score or 0.0) >= self.settings.retrieval_score_threshold
        ]
        return len(valid_chunks) >= self.settings.grounded_min_chunks

    @staticmethod
    def _score_from_distance(distance: float | None) -> float:
        if distance is None:
            return 0.0
        return max(0.0, 1.0 - float(distance))

    #解析向量库里的数据，组装成retrieved chunk格式，评分，排序
    def _parse_results(self, results: dict) -> list[RetrievedChunk]:
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        parsed: list[RetrievedChunk] = []
        for document, metadata, distance in zip(documents, metadatas, distances, strict=False):
            metadata = metadata or {}
            parsed.append(
                RetrievedChunk(
                    source=str(metadata.get("source", "unknown")),
                    file_type=metadata.get("file_type"),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                    content=str(document),
                    score=self._score_from_distance(distance),
                    distance=float(distance) if distance is not None else None,
                    start_offset=self._safe_int(metadata.get("start_offset")),
                    end_offset=self._safe_int(metadata.get("end_offset")),
                    title=self._safe_str(metadata.get("title")),
                    section=self._safe_str(metadata.get("section")),
                )
            )

        parsed.sort(key=lambda item: item.score, reverse=True)
        return parsed

    #过滤
    def _filter_by_score(self, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        return [chunk for chunk in chunks if chunk.score >= self.settings.retrieval_score_threshold]

    def _rrf_merge(
        self, vector_chunks: list[RetrievedChunk], bm25_chunks: list[RetrievedChunk]
    ) -> list[RetrievedChunk]:
        """Reciprocal Rank Fusion: score(d) = Σ weight / (k + rank)."""
        k = self.settings.rrf_k
        vector_w = self.settings.vector_weight
        bm25_w = self.settings.bm25_weight

        # Use (source, chunk_index) as dedup key 去重key
        scores: dict[tuple[str, int], float] = {}
        chunk_map: dict[tuple[str, int], RetrievedChunk] = {}

        for rank, chunk in enumerate(vector_chunks, start=1):
            key = (chunk.source, chunk.chunk_index)
            scores[key] = scores.get(key, 0.0) + vector_w / (k + rank)
            if key not in chunk_map:
                chunk_map[key] = chunk

        for rank, chunk in enumerate(bm25_chunks, start=1):
            key = (chunk.source, chunk.chunk_index)
            scores[key] = scores.get(key, 0.0) + bm25_w / (k + rank)
            if key not in chunk_map:
                chunk_map[key] = chunk

        sorted_keys = sorted(scores, key=lambda k_: scores[k_], reverse=True)
        merged: list[RetrievedChunk] = []
        for key in sorted_keys:
            chunk = chunk_map[key]
            merged.append(RetrievedChunk(
                source=chunk.source,
                file_type=chunk.file_type,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                score=scores[key],
                distance=chunk.distance,
                start_offset=chunk.start_offset,
                end_offset=chunk.end_offset,
                title=chunk.title,
                section=chunk.section,
            ))
        return merged

    def _apply_rerank(self, chunks: list[RetrievedChunk], question: str, rerank_n: int | None = None) -> list[RetrievedChunk]:
        if not chunks or self.reranker is None:
            return chunks
        top_n = rerank_n if rerank_n is not None else self.settings.rerank_top_n
        return self.reranker.rerank(query=question, chunks=chunks, top_n=top_n)

    def _select_prompt_chunks(self, chunks: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
        #去重，合并，字符预算
        deduped_chunks = self._dedupe_chunks(chunks)
        merged_chunks = self._merge_adjacent_chunks(deduped_chunks)
        return self._apply_context_budget(merged_chunks[:top_k])

    @staticmethod
    def _dedupe_chunks(chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        seen: set[tuple[str, int | None, int | None, str]] = set()
        deduped: list[RetrievedChunk] = []

        for chunk in chunks:
            key = (chunk.source, chunk.start_offset, chunk.end_offset, chunk.content.strip())
            if key in seen:
                continue
            seen.add(key)
            deduped.append(chunk)

        return deduped

    def _merge_adjacent_chunks(self, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        if not chunks:
            return []

        merged: list[RetrievedChunk] = []
        for chunk in chunks:
            if not merged:
                merged.append(chunk)
                continue

            previous = merged[-1]
            if self._can_merge(previous, chunk):
                merged[-1] = RetrievedChunk(
                    source=previous.source,
                    file_type=previous.file_type,
                    chunk_index=previous.chunk_index,
                    content=self._merge_content(previous.content, chunk.content),
                    score=max(previous.score, chunk.score),
                    distance=self._min_distance(previous.distance, chunk.distance),
                    start_offset=previous.start_offset,
                    end_offset=chunk.end_offset,
                    title=previous.title or chunk.title,
                    section=previous.section or chunk.section,
                )
                continue

            merged.append(chunk)

        return merged

    #合并的时候算距离
    @staticmethod
    def _min_distance(a: float | None, b: float | None) -> float | None:
        if a is None:
            return b
        if b is None:
            return a
        return min(a, b)

    #判断能否合并
    @staticmethod
    def _can_merge(left: RetrievedChunk, right: RetrievedChunk) -> bool:
        if left.source != right.source:
            return False
        if right.chunk_index != left.chunk_index + 1:
            return False
        if left.end_offset is None or right.start_offset is None or left.start_offset is None:
            return False
        return right.start_offset >= left.start_offset and right.start_offset - left.end_offset <= 80

    #合并
    @staticmethod
    def _merge_content(left: str, right: str) -> str:
        if right in left:
            return left
        if left in right:
            return right
        return f"{left.rstrip()}\n\n{right.lstrip()}"

    #裁剪
    def _apply_context_budget(self, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        if not chunks:
            return []

        selected: list[RetrievedChunk] = []
        used_chars = 0
        for chunk in chunks:
            chunk_cost = len(chunk.content) + 120
            if selected and used_chars + chunk_cost > self.settings.max_context_chars:
                break
            if not selected and chunk_cost > self.settings.max_context_chars:
                selected.append(
                    RetrievedChunk(
                        source=chunk.source,
                        file_type=chunk.file_type,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content[: max(self.settings.max_context_chars - 120, 0)].strip(),
                        score=chunk.score,
                        distance=chunk.distance,
                        start_offset=chunk.start_offset,
                        end_offset=chunk.end_offset,
                        title=chunk.title,
                        section=chunk.section,
                    )
                )
                break
            selected.append(chunk)
            used_chars += chunk_cost

        return selected

    #给llm的部分，上下文+内容
    @staticmethod
    def _build_context(chunks: list[RetrievedChunk]) -> str:
        context_parts: list[str] = []
        for idx, chunk in enumerate(chunks, start=1):
            context_parts.append(
                "\n".join(
                    [
                        f"[{idx}] source={chunk.source}",
                        f"file_type={chunk.file_type or 'unknown'}",
                        f"chunk_index={chunk.chunk_index}",
                        f"score={chunk.score:.3f}",
                        f"offsets={chunk.start_offset}-{chunk.end_offset}",
                        f"section={chunk.section or chunk.title or 'unknown'}",
                        "content:",
                        chunk.content,#实际文本内容
                    ]
                )
            )
        return "\n\n".join(context_parts)

    def _to_source_item(self, chunk: RetrievedChunk) -> SourceItem:
        return SourceItem(
            source=chunk.source,
            file_type=chunk.file_type,
            chunk_index=chunk.chunk_index,
            snippet=self._build_snippet(chunk.content),
            score=round(chunk.score, 4),
            distance=round(chunk.distance, 4) if chunk.distance is not None else None,
            start_offset=chunk.start_offset,
            end_offset=chunk.end_offset,
            title=chunk.title,
            section=chunk.section,
        )

    @staticmethod
    def _build_snippet(text: str, max_length: int = 240) -> str:
        cleaned = " ".join(text.split())
        if len(cleaned) <= max_length:
            return cleaned
        return f"{cleaned[: max_length - 1].rstrip()}…"

    @staticmethod
    def _safe_int(value: object) -> int | None:
        if value is None:
            return None
        return int(str(value))

    @staticmethod
    def _safe_str(value: object) -> str | None:
        if value is None:
            return None
        string_value = str(value).strip()
        return string_value or None
