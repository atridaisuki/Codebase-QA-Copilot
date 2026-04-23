# 项目知识说明

## 项目概览

Codebase QA Copilot 是一个最小化的 RAG 风格文档问答服务，基于 FastAPI、Chroma、本地 embedding 和 Claude 构建。

当前服务主要包含两个核心流程：

1. `POST /ingest`
   - 读取本地 `.md` 和 `.txt` 文件
   - 将文档切分为多个 chunk
   - 对 chunk 做向量化
   - 将结果写入 Chroma

2. `POST /qa`
   - 对用户问题生成向量
   - 从 Chroma 检索更多候选 chunk
   - 基于 score 阈值过滤低质量结果
   - 对结果做去重、相邻 chunk 合并和上下文预算裁剪
   - 基于检索质量判断当前证据是否充分
   - 若证据不足则返回 `根据当前文档无法确定。`
   - 若证据充分则基于检索上下文调用 Claude 生成回答

## 主要入口文件

- `app/main.py` —— 创建 FastAPI 应用并挂载路由
- `app/routers/health.py` —— 健康检查接口
- `app/routers/ingest.py` —— 文档入库接口
- `app/routers/qa.py` —— 问答接口

## 配置说明

`app/config.py` 使用 `pydantic-settings` 定义运行时配置。

关键配置包括：

- `default_docs_dir` —— 本地文档默认目录
- `chroma_persist_directory` —— Chroma 本地持久化目录
- `chroma_collection_name` —— Chroma collection 名称
- `embedding_model_name` —— sentence-transformers 的 embedding 模型
- `chunk_size` / `chunk_overlap` —— 文本切分参数
- `default_top_k` —— `/qa` 默认返回的 sources 数量
- `retrieval_fetch_k` —— 初召回数量，允许先多取再筛
- `retrieval_score_threshold` —— 最低有效检索分数阈值
- `grounded_top_score_threshold` —— grounded 判定所需的 top score 阈值
- `grounded_average_score_threshold` —— grounded 判定所需的平均分阈值
- `grounded_min_chunks` —— 过滤后最少有效 chunk 数
- `max_context_chars` —— 最终传给 prompt 的上下文预算
- `enable_rerank` / `rerank_top_n` —— 为后续 rerank 预留的配置
- `anthropic_api_key` —— 配置后可启用 Claude 生成
- `anthropic_model` —— 默认值为 `claude-opus-4-6`

## 核心请求流程

### Ingest 流程

位置：`app/routers/ingest.py`

1. 从请求参数或配置中解析 `docs_dir`。
2. 使用 `DocumentLoader` 加载文档。
3. 如果目录不存在，返回 `404`。
4. 如果没有找到支持的文档，返回 `400`。
5. 使用 `TextSplitter` 切分文本。
6. 使用 `EmbeddingService` 生成 chunk 向量。
7. 使用 `VectorStore` 写入 chunks 和 embeddings。
8. 返回文件数量、chunk 数量和 collection 名称。

### QA 流程

位置：`app/routers/qa.py`

1. 从请求参数或 `default_top_k` 解析 `top_k`。
2. 通过 `RetrievalService.retrieve()` 获取上下文和来源。
3. 如果当前没有已索引内容，返回 `400`。
4. 调用 `RetrievalService.has_sufficient_evidence()` 判断证据是否充分。
5. 如果证据较弱，返回 `根据当前文档无法确定。`，并设置 `grounded=false`。
6. 如果证据充分，则调用 `build_qa_prompt()` 生成 prompt。
7. 调用 `LLMService.generate_answer()` 获取回答。
8. 返回最终 answer、`grounded=true` 以及 source 元数据。

## 各服务模块职责

### `app/services/document_loader.py`
负责从磁盘加载支持的文档。

### `app/services/text_splitter.py`
负责优先按段落切分文本；当单段过长时，再退化为带 overlap 的窗口切块，并保留 `start_offset`、`end_offset`、`title`、`section` 等 metadata。

### `app/services/embedding_service.py`
负责封装文档与问题的本地向量生成逻辑。

### `app/services/vector_store.py`
负责封装 Chroma 的持久化、upsert 和相似度查询。

当前会在 metadata 中保存：
- `source`
- `file_type`
- `chunk_index`
- `start_offset`
- `end_offset`
- `title`
- `section`

查询时会同时取回 `documents`、`metadatas` 和 `distances`。

### `app/services/retrieval_service.py`
负责从向量检索结果中构造 QA 上下文和 source 列表。

关键行为：
- `retrieve()` 会先按 `retrieval_fetch_k` 做初召回，再进行 score 过滤。
- 检索结果会基于 `distance` 派生 `score = 1 - distance`，用于过滤、排序和返回。
- 在构造 prompt 前，会做去重、同源相邻 chunk 合并、上下文预算裁剪。
- `SourceItem` 会返回更完整的 metadata，包括 `file_type`、`score`、`distance`、`start_offset`、`end_offset`、`title`、`section`。
- `has_sufficient_evidence()` 现在主要基于 top score、average score 和有效 chunk 数做 grounded 判定，不再以 token overlap 作为核心逻辑。
- 代码中已经预留了 `初召回 -> 可选 rerank -> 最终上下文组装` 的结构，但当前默认不启用 rerank。

### `app/services/llm_service.py`
负责封装 Anthropic 调用逻辑。

关键行为：
- 当配置了 `ANTHROPIC_API_KEY` 时，会调用 `client.messages.create()`。
- 当未配置 API key 但存在 sources 时，会基于第一个检索结果返回确定性的抽取式 fallback 回答。
- 当未配置 API key 且没有 sources 时，会返回 `根据当前文档无法确定。`。

## Prompt 规则

`app/core/prompt_builder.py` 负责构造 grounded QA prompt。

当前约束目标是：
- 只能基于检索上下文回答
- 避免输出没有证据支持的内容
- 当文档无法支持回答时，需要明确表达不确定性

## 数据模型

`app/schemas.py` 定义了请求、响应以及内部元数据模型。

重要接口结构如下：

### Ingest 请求

```json
{
  "docs_dir": "data/docs"
}
```

### QA 请求

```json
{
  "question": "有哪些 API 可用？",
  "top_k": 3
}
```

### QA 响应

```json
{
  "answer": "...",
  "grounded": true,
  "sources": [
    {
      "source": "data/docs/product.md",
      "file_type": "md",
      "chunk_index": 0,
      "snippet": "POST /qa answers questions.",
      "score": 0.91,
      "distance": 0.09,
      "start_offset": 0,
      "end_offset": 42,
      "title": null,
      "section": "API"
    }
  ]
}
```

## 当前回答模式说明

目前系统有三种主要返回模式：

1. **没有已索引内容**
   - `/qa` 返回 HTTP `400`
   - 错误信息：`No indexed content found. Please ingest documents first.`

2. **已有索引，但证据不足**
   - `/qa` 返回 HTTP `200`
   - `answer` 为 `根据当前文档无法确定。`
   - `grounded` 为 `false`

3. **证据充分**
   - `/qa` 返回 HTTP `200`
   - `answer` 由 Claude 或 fallback 逻辑生成
   - `grounded` 为 `true`

## 测试文件说明

### `tests/test_health.py`
覆盖健康检查接口行为。

### `tests/test_loader.py`
覆盖文档加载行为。

### `tests/test_splitter.py`
覆盖段落优先切分、超长段落降级切分、offset metadata 和稳定 chunk id。

### `tests/test_ingest.py`
覆盖 ingest 接口行为，包括：
- 正常入库
- 无支持文档时的返回
- 缺失目录时返回 `404`

### `tests/test_qa.py`
覆盖 QA 行为，包括：
- 没有已索引内容时返回 `400`
- 证据不足时返回 `根据当前文档无法确定。`
- grounded 回答时返回带 score 和 metadata 的 sources
- 未传 `top_k` 时回退到 `default_top_k`
- 未配置 Anthropic API key 时 `LLMService` 的 fallback 行为

### `tests/test_retrieval_service.py`
覆盖 retrieval v2 的核心逻辑，包括：
- 分数过滤
- 相邻 chunk 合并
- 上下文预算裁剪
- grounded 判定
- score/source metadata 构造

## 当前实现注意事项

- 当前应用是刻意保持最小化、偏本地运行的实现。
- 仅支持索引 `.md` 和 `.txt` 文件。
- Chroma 数据保存在本地。
- Claude 生成在运行时是可选的，因为系统提供了抽取式 fallback。
- 默认 Claude 模型为 `claude-opus-4-6`。

## 后续维护建议优先查看的文件

- `app/routers/qa.py`
- `app/services/llm_service.py`
- `app/services/retrieval_service.py`
- `app/routers/ingest.py`
- `app/config.py`
- `tests/test_qa.py`
- `tests/test_ingest.py`
