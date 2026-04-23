from __future__ import annotations

import json
from typing import Any

from app.services.retrieval_service import RetrievalService

AGENT_SYSTEM_PROMPT = """你是一个智能知识库助手。你可以使用以下工具来回答用户的问题：

1. knowledge_search — 搜索知识库，获取与查询相关的文档片段
2. list_documents — 列出知识库中所有已索引的文档
3. get_document_outline — 获取指定文档的章节大纲

工作原则：
- 如果用户的问题是闲聊或不需要知识库的，直接回答即可，不必调用工具。
- 如果需要查找信息，先用 knowledge_search 搜索。
- 如果需要比较多个主题，可以多次调用 knowledge_search，每次用不同的查询词。
- 如果不确定知识库里有什么文档，先用 list_documents 查看。
- 如果需要了解某个文档的结构，用 get_document_outline。
- 基于工具返回的内容回答问题，引用来源时使用文件名。
- 如果知识库中没有相关信息，如实告知用户。
"""

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "knowledge_search",
        "description": "搜索知识库，返回与查询最相关的文档片段。支持语义搜索和关键词混合检索。",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询词，尽量具体以获得更精准的结果",
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回的最大结果数量，默认3",
                    "default": 3,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "list_documents",
        "description": "列出知识库中所有已索引的文档名称。用于了解知识库覆盖范围。",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_document_outline",
        "description": "获取指定文档的章节大纲，了解文档结构。",
        "input_schema": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "文档路径，例如 data/docs/python.md",
                },
            },
            "required": ["source"],
        },
    },
]


def execute_tool(
    tool_name: str,
    tool_input: dict[str, Any],
    retrieval_service: RetrievalService,
) -> tuple[str, list[dict[str, Any]]]:
    """Execute a tool and return (result_text, sources_list)."""
    if tool_name == "knowledge_search":
        return _execute_knowledge_search(tool_input, retrieval_service)
    if tool_name == "list_documents":
        return _execute_list_documents(retrieval_service)
    if tool_name == "get_document_outline":
        return _execute_get_document_outline(tool_input, retrieval_service)
    return f"Unknown tool: {tool_name}", []


def _execute_knowledge_search(
    tool_input: dict[str, Any],
    retrieval_service: RetrievalService,
) -> tuple[str, list[dict[str, Any]]]:
    query = str(tool_input.get("query", ""))
    top_k = int(tool_input.get("top_k", 3))
    context, sources = retrieval_service.retrieve(query, top_k=top_k)
    if not context:
        return "未找到相关内容。", []
    source_dicts = [s.model_dump() if hasattr(s, "model_dump") else s for s in sources]
    return context, source_dicts


def _execute_list_documents(
    retrieval_service: RetrievalService,
) -> tuple[str, list[dict[str, Any]]]:
    sources = retrieval_service.list_sources()
    if not sources:
        return "知识库中暂无文档。", []
    return "已索引的文档：\n" + "\n".join(f"- {s}" for s in sources), []


def _execute_get_document_outline(
    tool_input: dict[str, Any],
    retrieval_service: RetrievalService,
) -> tuple[str, list[dict[str, Any]]]:
    source = str(tool_input.get("source", ""))
    sections = retrieval_service.get_sections(source)
    if not sections:
        return f"未找到文档 {source} 的大纲信息。", []
    lines = [f"文档 {source} 的大纲："]
    for s in sections:
        section_name = s.get("section") or "(无标题)"
        lines.append(f"- chunk {s.get('chunk_index')}: {section_name}")
    return "\n".join(lines), []
