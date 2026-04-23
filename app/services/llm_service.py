from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

import anthropic

from app.config import get_settings
from app.schemas import SourceItem

if TYPE_CHECKING:
    from anthropic.types import MessageParam


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client: anthropic.Anthropic | None = None
        self.uses_custom_base_url = bool(self.settings.anthropic_base_url)
        if self.settings.anthropic_api_key:
            kwargs: dict[str, Any] = {"api_key": self.settings.anthropic_api_key}
            if self.settings.anthropic_base_url:
                kwargs["base_url"] = self.settings.anthropic_base_url
            self.client = anthropic.Anthropic(**kwargs)

    def generate_answer(self, prompt: str, sources: list[SourceItem] | None = None) -> str:
        if not self.client:
            if sources:
                return self._build_fallback_answer(sources)
            return "根据当前文档无法确定。"

        messages: list[MessageParam] = [{"role": "user", "content": prompt}]

        if self.uses_custom_base_url:
            response = self.client.messages.create(
                model=self.settings.anthropic_model,
                max_tokens=1024,
                messages=messages,
            )
        else:
            response = self.client.messages.create(
                model=self.settings.anthropic_model,
                max_tokens=1024,
                extra_body={
                    "thinking": {"type": "adaptive"},
                    "output_config": {"effort": "high"},
                },
                messages=messages,
            )

        texts = [block.text for block in response.content if block.type == "text"]
        return "\n".join(texts).strip() or "根据当前文档无法确定。"

    @staticmethod
    def _build_fallback_answer(sources: Sequence[SourceItem | dict[str, Any]]) -> str:
        primary_source = sources[0]
        if isinstance(primary_source, dict):
            source = str(primary_source.get("source", "unknown"))
            chunk_index = int(primary_source.get("chunk_index", 0))
            snippet = str(primary_source.get("snippet", ""))
        else:
            source = primary_source.source
            chunk_index = primary_source.chunk_index
            snippet = primary_source.snippet

        return f"Anthropic API key is not configured. Grounded excerpt from {source} (chunk {chunk_index}): {snippet}"
