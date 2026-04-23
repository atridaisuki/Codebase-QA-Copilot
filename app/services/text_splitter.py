import hashlib
import re

from app.config import get_settings
from app.schemas import ChunkRecord, DocumentRecord


class TextSplitter:
    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None) -> None:
        settings = get_settings()
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

    def split_documents(self, documents: list[DocumentRecord]) -> list[ChunkRecord]:
        chunks: list[ChunkRecord] = []
        for document in documents:
            chunks.extend(self._split_document(document))
        return chunks

    def _split_document(self, document: DocumentRecord) -> list[ChunkRecord]:
        text = document.content
        if not text.strip():
            return []

        segments = self._split_into_segments(text)
        chunk_payloads: list[dict] = []
        current_parts: list[str] = []
        current_start: int | None = None
        current_end = 0

        for segment in segments:
            segment_text = segment["text"].strip()
            if not segment_text:
                continue

            if len(segment_text) > self.chunk_size:
                if current_parts:
                    chunk_payloads.append(self._build_chunk_payload(current_parts, current_start or 0, current_end))
                    current_parts = []
                    current_start = None
                chunk_payloads.extend(self._split_long_segment(segment))
                continue

            proposed_text = self._join_parts(current_parts + [segment_text])
            if current_parts and len(proposed_text) > self.chunk_size:
                chunk_payloads.append(self._build_chunk_payload(current_parts, current_start or 0, current_end))
                current_parts = [segment_text]
                current_start = int(segment["start"])
                current_end = int(segment["end"])
                continue

            current_parts.append(segment_text)
            current_start = int(segment["start"]) if current_start is None else current_start
            current_end = int(segment["end"])

        if current_parts:
            chunk_payloads.append(self._build_chunk_payload(current_parts, current_start or 0, current_end))

        return [self._to_chunk_record(document, index, payload) for index, payload in enumerate(chunk_payloads)]

    @staticmethod
    def _split_into_segments(text: str) -> list[dict]:
        matches = list(re.finditer(r"\n\s*\n+", text))
        segments: list[dict] = []
        start = 0

        for match in matches:
            end = match.start()
            segment_text = text[start:end]
            if segment_text.strip():
                segments.append({"text": segment_text, "start": start, "end": end})
            start = match.end()

        tail = text[start:]
        if tail.strip():
            segments.append({"text": tail, "start": start, "end": len(text)})

        if not segments:
            stripped = text.strip()
            if stripped:
                start_offset = text.index(stripped)
                segments.append({"text": stripped, "start": start_offset, "end": start_offset + len(stripped)})

        return segments

    def _split_long_segment(self, segment: dict) -> list[dict]:
        text = str(segment["text"])
        base_start = int(segment["start"])
        step = self.chunk_size - self.chunk_overlap
        pieces: list[dict] = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            raw_piece = text[start:end]
            stripped_piece = raw_piece.strip()
            if stripped_piece:
                leading_ws = len(raw_piece) - len(raw_piece.lstrip())
                trailing_ws = len(raw_piece) - len(raw_piece.rstrip())
                piece_start = base_start + start + leading_ws
                piece_end = base_start + end - trailing_ws
                pieces.append(
                    {
                        "content": stripped_piece,
                        "start_offset": piece_start,
                        "end_offset": piece_end,
                        "title": None,
                        "section": None,
                    }
                )
            if end >= len(text):
                break
            start += step

        return pieces

    @staticmethod
    def _join_parts(parts: list[str]) -> str:
        return "\n\n".join(part.strip() for part in parts if part.strip()).strip()

    def _build_chunk_payload(self, parts: list[str], start_offset: int, end_offset: int) -> dict:
        content = self._join_parts(parts)
        title = self._extract_title(parts)
        section = self._extract_section(parts)
        return {
            "content": content,
            "start_offset": start_offset,
            "end_offset": end_offset,
            "title": title,
            "section": section,
        }

    @staticmethod
    def _extract_title(parts: list[str]) -> str | None:
        if not parts:
            return None
        first_line = next((line.strip() for line in parts[0].splitlines() if line.strip()), "")
        if first_line.startswith("#"):
            return first_line.lstrip("#").strip() or None
        return None

    def _extract_section(self, parts: list[str]) -> str | None:
        for part in parts:
            for line in part.splitlines():
                candidate = line.strip()
                if not candidate:
                    continue
                if candidate.startswith("#"):
                    return candidate.lstrip("#").strip() or None
                if len(candidate) <= 120 and candidate.endswith(":"):
                    return candidate[:-1].strip() or None
        return self._extract_title(parts)

    @staticmethod
    def _stable_chunk_id(source: str, start_offset: int, end_offset: int, content: str) -> str:
        digest = hashlib.md5(f"{source}:{start_offset}:{end_offset}:{content}".encode()).hexdigest()[:12]
        return f"{source}:{start_offset}:{end_offset}:{digest}"

    def _to_chunk_record(self, document: DocumentRecord, chunk_index: int, payload: dict) -> ChunkRecord:
        return ChunkRecord(
            id=self._stable_chunk_id(
                document.source,
                int(payload["start_offset"]),
                int(payload["end_offset"]),
                str(payload["content"]),
            ),
            source=document.source,
            file_type=document.file_type,
            chunk_index=chunk_index,
            content=str(payload["content"]),
            start_offset=int(payload["start_offset"]),
            end_offset=int(payload["end_offset"]),
            title=payload.get("title"),
            section=payload.get("section"),
        )
