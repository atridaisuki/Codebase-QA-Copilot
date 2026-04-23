from __future__ import annotations

import uuid
from collections import OrderedDict
from typing import Any


class ConversationStore:
    """In-memory LRU conversation store keyed by conversation_id."""

    def __init__(self, max_size: int = 128) -> None:
        self._max_size = max_size
        self._store: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()

    def create(self) -> str:
        cid = uuid.uuid4().hex[:12]
        self._store[cid] = []
        self._evict()
        return cid

    def get(self, conversation_id: str) -> list[dict[str, Any]] | None:
        if conversation_id not in self._store:
            return None
        self._store.move_to_end(conversation_id)
        return self._store[conversation_id]

    def append(self, conversation_id: str, messages: list[dict[str, Any]]) -> None:
        if conversation_id not in self._store:
            self._store[conversation_id] = []
        self._store[conversation_id].extend(messages)
        self._store.move_to_end(conversation_id)
        self._evict()

    def _evict(self) -> None:
        while len(self._store) > self._max_size:
            self._store.popitem(last=False)


# Module-level singleton
conversation_store = ConversationStore()
