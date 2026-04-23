# Codebase QA Copilot V1 实施方案

## 1. 目标

构建一个基于 FastAPI + Chroma + Claude 的最小化文档问答系统，具备以下能力：

- 读取本地 `.md` 和 `.txt` 文档
- 将文档切分为多个 chunk
- 生成向量并存入 Chroma
- 根据用户问题检索相关片段
- 基于检索结果生成回答
- 返回可追溯的来源引用

## 2. 范围

### V1 范围内
- 从指定目录加载本地文档
- 递归读取 Markdown/TXT 文件
- 支持可配置的 chunk 大小与重叠长度
- 使用 `sentence-transformers` 进行本地向量化
- 使用 ChromaDB 做本地持久化向量存储
- 提供 FastAPI 的 health、ingest、qa 接口
- 返回带来源的回答结果
- 提供基础测试覆盖 health、loader、splitter

### V1 暂不包含
- 用户认证
- 多租户隔离
- 后台异步任务
- 重排序（re-ranking）
- OCR / PDF 解析
- 前端 UI
- 高级可观测性能力

## 3. 技术栈

- **API 框架**：FastAPI
- **配置管理**：pydantic-settings
- **向量库**：ChromaDB
- **Embedding 模型**：`sentence-transformers/all-MiniLM-L6-v2`
- **LLM**：Anthropic Python SDK（`claude-opus-4-6`）
- **测试框架**：pytest

## 4. 项目结构

```text
app/
  core/
    prompt_builder.py
  routers/
    health.py
    ingest.py
    qa.py
  services/
    document_loader.py
    text_splitter.py
    embedding_service.py
    vector_store.py
    retrieval_service.py
    llm_service.py
  config.py
  main.py
  schemas.py

data/
  docs/

docs/
  v1-implementation-plan.md

tests/
  test_health.py
  test_loader.py
  test_splitter.py

.env.example
README.md
requirements.txt
```

## 5. 模块职责

### `app/config.py`
集中管理运行时配置，例如文档目录、Chroma 路径、chunk 参数、embedding 模型和 Claude 模型。

### `app/schemas.py`
定义接口的请求/响应模型，以及内部使用的文档与 chunk 元数据结构。

### `app/services/document_loader.py`
递归扫描目录，读取 `.md` / `.txt` 文件，并转成统一的文档对象。

### `app/services/text_splitter.py`
将文档切分成带重叠的 chunk，并附带来源元数据。

### `app/services/embedding_service.py`
提供统一的向量化接口：
- `embed_documents(texts)`
- `embed_query(text)`

### `app/services/vector_store.py`
封装 Chroma collection 的创建、写入与相似度检索。

### `app/services/retrieval_service.py`
检索 top-k chunk，并整理出 prompt 用上下文与接口返回所需的 sources。

### `app/core/prompt_builder.py`
构造严格要求“基于检索上下文回答”的 RAG prompt。

### `app/services/llm_service.py`
通过 Anthropic SDK 调用 Claude；当未配置 API key 时，回退到确定性的抽取式回答，保证应用仍可运行。

### 路由
- `/health`：服务健康检查
- `/ingest`：构建或刷新向量索引
- `/qa`：检索上下文并回答问题

## 6. API 设计

### `GET /health`
返回服务健康状态和基础信息。

示例响应：

```json
{
  "status": "ok",
  "service": "codebase-qa-copilot"
}
```

### `POST /ingest`
请求：

```json
{
  "docs_dir": "data/docs"
}
```

响应：

```json
{
  "files_count": 2,
  "chunks_count": 8,
  "collection_name": "documents"
}
```

### `POST /qa`
请求：

```json
{
  "question": "产品支持什么功能？",
  "top_k": 3
}
```

响应：

```json
{
  "answer": "...",
  "sources": [
    {
      "source": "data/docs/product.md",
      "chunk_index": 0,
      "snippet": "..."
    }
  ]
}
```

## 7. 开发步骤

1. 编写实施说明 Markdown 文档。
2. 创建依赖文件与环境变量模板。
3. 搭建 FastAPI 应用骨架和 health 路由。
4. 实现文档加载能力。
5. 实现文本切分。
6. 实现 embedding 服务。
7. 实现 Chroma 向量存储。
8. 实现检索结果整理逻辑。
9. 实现 prompt 构造器。
10. 实现基于 Claude 的回答生成逻辑。
11. 增加 ingest 和 qa 接口。
12. 增加示例文档。
13. 增加测试并验证应用可启动。

## 8. 本地运行

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Swagger 地址：
- `http://127.0.0.1:8000/docs`

## 9. 验收标准

V1 版本满足以下条件即可视为完成：

- FastAPI 应用可以正常启动
- `/health` 能返回 OK
- `/ingest` 可以索引本地 Markdown/TXT 文件
- `/qa` 能基于检索上下文回答问题
- `/qa` 响应中包含 `sources`
- 当证据不足时，系统会明确表示当前文档无法确定，而不是编造答案
- health、loader、splitter 的测试可以通过

## 10. 验证清单

### 启动验证
- 安装依赖
- 运行 `uvicorn app.main:app --reload`
- 打开 `/docs` 与 `/health`

### 索引验证
- 在 `data/docs/` 中放入示例文件
- 调用 `POST /ingest`
- 检查 `files_count` 和 `chunks_count`

### QA 验证
- 调用 `POST /qa`
- 检查回答是否基于已索引文档
- 检查是否返回 sources
- 检查对无依据问题不会产生幻觉式回答

### 测试验证
- 运行 `pytest`
- 确认没有语法或导入错误
