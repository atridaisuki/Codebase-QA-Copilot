# V4 开发计划：Agent 能力

> 目标：在现有 RAG 基础上加一层 Agent，让 LLM 自主决定是否需要检索、检索什么、检索几次，支持多步推理和流式输出。

核心原则：复用现有检索 pipeline，不重写；用 Claude 原生 tool_use，不造轮子。

---

## 架构

```
POST /agent/chat
      │
      ▼
  构建 messages（system prompt + 对话历史 + 用户消息）
      │
      ▼
  ┌─► 调用 Claude（带 tools 定义）─────────────────┐
  │        │                                        │
  │        ▼                                        │
  │   Claude 返回：                                  │
  │   ├─ 纯文本 → 结束，输出最终回答                   │
  │   └─ tool_use → 执行工具，结果喂回 Claude          │
  │             │                                    │
  └─────────────┘  （最多循环 5 次）
```

---

## 工具定义（3 个）

| 工具 | 作用 | 底层调用 |
|------|------|---------|
| `knowledge_search` | 搜索知识库 | `RetrievalService.retrieve()` |
| `list_documents` | 列出所有文档 | `VectorStore.get_all_metadata()` |
| `get_document_outline` | 获取文档大纲 | VectorStore metadata 按 source 过滤 |

`knowledge_search` 复用整个现有 pipeline（hybrid + rerank + grounding），零重复代码。

---

## 实现步骤

### Step 1：Schemas + Config

**`app/schemas.py`** — 新增 4 个 schema：

```python
class ChatMessage(BaseModel):
    role: str
    content: str

class ToolStep(BaseModel):
    tool_name: str
    tool_input: dict[str, Any]
    tool_result: str

class AgentRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None

class AgentResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: list[SourceItem]
    tool_steps: list[ToolStep]
```

**`app/config.py`** — 新增 2 个配置项：

```python
agent_max_iterations: int = Field(default=5)
agent_max_tokens: int = Field(default=2048)
```

### Step 2：工具定义

**新建 `app/services/agent_tools.py`**

包含：
- `AGENT_SYSTEM_PROMPT` — 指导 Claude 何时调用工具、如何回答
- `TOOL_DEFINITIONS` — 3 个工具的 Claude tool_use schema
- `execute_tool()` — 分发函数，根据 tool_name 调用对应实现
- `_execute_knowledge_search()` — 调用 `RetrievalService.retrieve()`
- `_execute_list_documents()` — 调用 `RetrievalService.list_sources()`
- `_execute_get_document_outline()` — 调用 `RetrievalService.get_sections()`

### Step 3：VectorStore 辅助方法

**`app/services/vector_store.py`** — 新增：

```python
def get_all_metadata(self) -> list[dict[str, Any]]:
    result = self.collection.get(include=["metadatas"])
    return list(result.get("metadatas") or [])
```

**`app/services/retrieval_service.py`** — 新增：

```python
def list_sources(self) -> list[str]:
    # 从 VectorStore 获取所有 metadata，提取去重后的 source 列表

def get_sections(self, source: str) -> list[dict[str, str | int | None]]:
    # 按 source 过滤 metadata，返回 section + chunk_index 列表
```

### Step 4：对话存储

**新建 `app/core/conversation_store.py`**

- `ConversationStore` 类，基于 `OrderedDict` 实现 LRU（默认 max_size=128）
- 方法：`create()` → 生成 conversation_id，`get()` → 获取历史，`append()` → 追加消息
- 模块级单例 `conversation_store`

### Step 5：Agent 核心（重点）

**新建 `app/services/agent_service.py`**

`AgentService` 类，核心方法：

- `chat(message, conversation_id)` → `AgentResponse`
  - 解析或创建 conversation_id
  - 构建 messages（历史 + 新消息）
  - ReAct 循环（最多 `agent_max_iterations` 次）：
    - 调用 `client.messages.create()` 带 tools
    - 若 `stop_reason == "end_turn"` → 提取文本，结束
    - 若 `stop_reason == "tool_use"` → 执行工具，拼 tool_result，继续循环
  - 收集所有 knowledge_search 的 sources，去重
  - 持久化对话历史

- `chat_stream(message, conversation_id)` → `Generator[dict]`
  - 同样的 ReAct 循环
  - tool_call / tool_result 阶段同步执行，yield SSE 事件
  - 最终回答阶段 yield text 事件
  - 最后 yield done 事件（含 conversation_id、sources、tool_steps）

辅助方法：
- `_process_tool_calls()` — 遍历 content blocks，执行 tool_use 类型的 block
- `_serialize_content()` — 将 Claude response content 序列化为 dict 列表（用于 messages 拼接）
- `_extract_text()` — 从 content blocks 中提取纯文本
- `_dedupe_sources()` — 按 (source, chunk_index) 去重

### Step 6：路由

**新建 `app/routers/agent.py`**

```python
router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/chat", response_model=AgentResponse)
def agent_chat(request: AgentRequest) -> AgentResponse

@router.post("/chat/stream")
def agent_chat_stream(request: AgentRequest) -> EventSourceResponse
```

**`app/main.py`** — 注册 agent router：

```python
from app.routers.agent import router as agent_router
app.include_router(agent_router, prefix=settings.api_prefix)
```

### Step 7：SSE 流式输出

- 依赖 `sse-starlette`（已添加到 `pyproject.toml`）
- SSE 事件类型：
  - `tool_call` — `{"tool_name": "...", "tool_input": {...}}`
  - `tool_result` — `{"tool_name": "...", "result_preview": "前200字符"}`
  - `text` — 最终回答文本
  - `done` — `{"conversation_id": "...", "sources": [...], "tool_steps": [...]}`

### Step 8：测试

**新建 `tests/test_agent.py`** — 7 个测试用例：

| 测试 | 验证内容 |
|------|---------|
| `test_agent_direct_answer` | Claude 直接回答，不调工具 |
| `test_agent_single_search` | 单次 knowledge_search |
| `test_agent_multi_step_search` | 两次 knowledge_search（不同查询） |
| `test_agent_max_iterations` | 达到 max_iterations 后停止 |
| `test_agent_sse_stream` | SSE 事件顺序正确 |
| `test_agent_multi_turn` | conversation_id 多轮对话 |
| `test_agent_list_documents_tool` | list_documents 工具调用 |

测试模式：monkeypatch 替换 `RetrievalService`、`anthropic.Anthropic`、`get_settings`，用 stub 类模拟 Claude 响应。

---

## 文件清单

| 操作 | 文件 |
|------|------|
| 新建 | `app/services/agent_service.py` |
| 新建 | `app/services/agent_tools.py` |
| 新建 | `app/routers/agent.py` |
| 新建 | `app/core/conversation_store.py` |
| 新建 | `tests/test_agent.py` |
| 修改 | `app/schemas.py` — 新增 Agent 相关 schema |
| 修改 | `app/config.py` — 新增 agent 配置项 |
| 修改 | `app/main.py` — 注册 agent router |
| 修改 | `app/services/vector_store.py` — 新增 `get_all_metadata()` |
| 修改 | `app/services/retrieval_service.py` — 新增 `list_sources()`, `get_sections()` |
| 修改 | `pyproject.toml` — 添加 `sse-starlette` 依赖 |

现有 `/qa` 端点完全不动，向后兼容。

---

## 验证方式

```bash
# 1. 直接回答（不触发工具）
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'

# 2. 单次检索
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Docker是什么？"}'

# 3. 多步推理（应触发 2+ 次 knowledge_search）
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "比较GIL和Redis单线程模型的异同"}'

# 4. SSE 流式
curl -N -X POST http://localhost:8000/agent/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "什么是GIL？"}'

# 5. 多轮对话（用返回的 conversation_id）
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "那它有什么缺点？", "conversation_id": "<id>"}'

# 6. 跑测试
python -m pytest tests/test_agent.py -v
```

---

## 测试结果

全部 7 个 agent 测试通过，现有 40 个测试不受影响（1 个 pre-existing failure 与 V4 无关）。
