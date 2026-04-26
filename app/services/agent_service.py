from __future__ import annotations

import json
import logging
from collections.abc import Generator
from typing import Any

import anthropic

from app.config import get_settings
from app.core.conversation_store import conversation_store
from app.schemas import AgentResponse, SourceItem, ToolStep
from app.services.agent_tools import (
    AGENT_SYSTEM_PROMPT,
    TOOL_DEFINITIONS,
    execute_tool,
)
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.retrieval_service = RetrievalService()
        self.client: anthropic.Anthropic | None = None
        if self.settings.anthropic_api_key:
            kwargs: dict[str, Any] = {"api_key": self.settings.anthropic_api_key}
            if self.settings.anthropic_base_url:
                kwargs["base_url"] = self.settings.anthropic_base_url
            self.client = anthropic.Anthropic(**kwargs)

    def chat(self, message: str, conversation_id: str | None = None) -> AgentResponse:
        if not self.client:
            return AgentResponse(
                conversation_id=conversation_id or "",
                answer="Anthropic API key is not configured.",
                sources=[],
                tool_steps=[],
            )

        # Resolve or create conversation
        if conversation_id:
            history = conversation_store.get(conversation_id)
            if history is None:
                conversation_id = conversation_store.create()
                history = []
        else:
            conversation_id = conversation_store.create()
            history = []

        # Build messages
        messages: list[dict[str, Any]] = list(history)
        messages.append({"role": "user", "content": message})

        all_sources: list[dict[str, Any]] = []
        tool_steps: list[ToolStep] = []

        #react循环
        for _ in range(self.settings.agent_max_iterations):
            response = self.client.messages.create(
                model=self.settings.anthropic_model,
                max_tokens=self.settings.agent_max_tokens,
                system=AGENT_SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

            # Append assistant response to messages
            assistant_content = self._serialize_content(response.content)
            messages.append({"role": "assistant", "content": assistant_content})

            if response.stop_reason != "tool_use":
                # Final answer
                answer = self._extract_text(response.content)
                break
            # Process tool calls
            tool_results = self._process_tool_calls(
                response.content, all_sources, tool_steps
            )
            messages.append({"role": "user", "content": tool_results})
        else:
            answer = self._extract_text(response.content)#如果5轮下来都没结果

        # Persist conversation
        new_messages = messages[len(history):]
        conversation_store.append(conversation_id, new_messages)

        # 去重 & 返回
        sources = self._dedupe_sources(all_sources)
        return AgentResponse(
            conversation_id=conversation_id,
            answer=answer,
            sources=sources,
            tool_steps=tool_steps,
        )

    def chat_stream(
        self, message: str, conversation_id: str | None = None
    ) -> Generator[dict[str, Any], None, None]:
        """Yield SSE-compatible event dicts."""
        if not self.client:
            yield {"event": "text", "data": "Anthropic API key is not configured."}
            yield {"event": "done", "data": json.dumps({"conversation_id": ""})}
            return

        if conversation_id:
            history = conversation_store.get(conversation_id)
            if history is None:
                conversation_id = conversation_store.create()
                history = []
        else:
            conversation_id = conversation_store.create()
            history = []

        messages: list[dict[str, Any]] = list(history)
        messages.append({"role": "user", "content": message})

        all_sources: list[dict[str, Any]] = []
        tool_steps: list[ToolStep] = []
        final_iteration = False

        for _ in range(self.settings.agent_max_iterations):
            if final_iteration:
                break

            response = self.client.messages.create(
                model=self.settings.anthropic_model,
                max_tokens=self.settings.agent_max_tokens,
                system=AGENT_SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

            assistant_content = self._serialize_content(response.content)
            messages.append({"role": "assistant", "content": assistant_content})

            if response.stop_reason != "tool_use":
                # Stream the final text
                text = self._extract_text(response.content)
                # For streaming, yield text in chunks
                yield {"event": "text", "data": text}
                final_iteration = True
            else:
                tool_results = self._process_tool_calls(
                    response.content, all_sources, tool_steps
                )
                # Yield tool events
                for step in tool_steps[len(tool_steps) - self._count_tool_uses(response.content):]:
                    yield {
                        "event": "tool_call",
                        "data": json.dumps(
                            {"tool_name": step.tool_name, "tool_input": step.tool_input},
                            ensure_ascii=False,
                        ),
                    }
                    yield {
                        "event": "tool_result",
                        "data": json.dumps(
                            {"tool_name": step.tool_name, "result_preview": step.tool_result[:200]},
                            ensure_ascii=False,
                        ),
                    }
                messages.append({"role": "user", "content": tool_results})

        # Persist conversation
        new_messages = messages[len(history):]
        conversation_store.append(conversation_id, new_messages)

        sources = self._dedupe_sources(all_sources)
        yield {
            "event": "done",
            "data": json.dumps(
                {
                    "conversation_id": conversation_id,
                    "sources": [s.model_dump() for s in sources],
                    "tool_steps": [s.model_dump() for s in tool_steps],
                },
                ensure_ascii=False,
            ),
        }

    def _process_tool_calls(
        self,
        content: list[Any],
        all_sources: list[dict[str, Any]],
        tool_steps: list[ToolStep],
    ) -> list[dict[str, Any]]:
        tool_results: list[dict[str, Any]] = []
        for block in content:
            if block.type != "tool_use":
                continue
            tool_name = block.name
            tool_input = dict(block.input) if block.input else {}
            logger.info("Executing tool: %s with input: %s", tool_name, tool_input)

            result_text, sources = execute_tool(
                tool_name, tool_input, self.retrieval_service
            )
            all_sources.extend(sources)
            tool_steps.append(
                ToolStep(
                    tool_name=tool_name,
                    tool_input=tool_input,
                    tool_result=result_text,
                )
            )
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_text,
                }
            )
        return tool_results

    @staticmethod
    def _serialize_content(content: list[Any]) -> list[dict[str, Any]]:
        serialized: list[dict[str, Any]] = []
        for block in content:
            if block.type == "text":
                serialized.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                serialized.append(
                    {
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": dict(block.input) if block.input else {},
                    }
                )
        return serialized

    @staticmethod
    def _extract_text(content: list[Any]) -> str:
        texts = [block.text for block in content if block.type == "text"]
        return "\n".join(texts).strip()

    @staticmethod
    def _count_tool_uses(content: list[Any]) -> int:
        return sum(1 for block in content if block.type == "tool_use")

    @staticmethod
    def _dedupe_sources(source_dicts: list[dict[str, Any]]) -> list[SourceItem]:
        seen: set[tuple[str, int]] = set()
        result: list[SourceItem] = []
        for d in source_dicts:
            key = (d.get("source", ""), d.get("chunk_index", 0))
            if key in seen:
                continue
            seen.add(key)
            result.append(SourceItem(**d))
        return result
