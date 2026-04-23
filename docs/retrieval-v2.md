# Retrieval V2 升级说明

## 1. 背景

当前项目在 V1 阶段已经具备最小可用的 RAG 闭环：

- `POST /ingest`：负责文档加载、切块、向量化并写入 Chroma
- `POST /qa`：负责问题向量化、检索、拼接上下文并调用 LLM 回答

V1 的主链路已经清晰，但整体仍偏 MVP：

- 固定字符窗口切块
- 单路向量召回后直接拼接 top-k
- 不暴露 score / distance
- 无低质量过滤
- 无去重 / 合并
- grounded 判断依赖脆弱的 token overlap
- sources 引用信息较少

本次 Retrieval V2 的目标是在**不明显增加系统复杂度**的前提下，优先提升：

- 召回命中率
- 上下文质量
- 引用质量
- grounded 判断稳定性
- 回答可解释性

同时保留现有主链路：

`/ingest -> VectorStore -> RetrievalService -> /qa`

---

## 2. 本次升级范围

本次 V2 已实现以下内容：

1. 检索结果增加 `distance` / `score`
2. `SourceItem` 增强，返回更完整 metadata
3. 新增 retrieval 相关配置项
4. 在 `RetrievalService` 中增加低质量过滤
5. 将切块策略从固定字符窗升级为“优先段落切分，超长再降级切块”
6. 为 chunk 增加 offset / section 等 metadata
7. 增加检索后处理：去重、相邻 chunk 合并、上下文预算控制
8. 用检索质量判定替代 token-overlap 作为 grounded 核心逻辑
9. 为 rerank 预留结构和配置，但本轮不引入新依赖
10. 为 splitter / retrieval / qa 增加测试覆盖

---

## 3. 关键改动文件

### 核心实现文件

- `app/config.py`
- `app/schemas.py`
- `app/services/vector_store.py`
- `app/services/text_splitter.py`
- `app/services/retrieval_service.py`
- `app/core/prompt_builder.py`
- `app/routers/qa.py`

### 测试文件

- `tests/test_splitter.py`
- `tests/test_retrieval_service.py`
- `tests/test_qa.py`

---

## 4. 具体实现说明

### 4.1 检索结果增加 score / distance

位置：`app/services/vector_store.py`

#### 变更点

- `VectorStore.query()` 现在会显式请求：
  - `documents`
  - `metadatas`
  - `distances`
- `RetrievalService` 会从 Chroma 查询结果中解析 `distance`
- 当前使用 `score = 1 - distance` 的简单映射，供：
  - 过滤
  - 排序
  - 接口返回
  - 调试观察

#### 价值

- 可做低质量过滤
- 可调试检索排序
- 可向前端暴露相关度信号
- 可作为 grounded 判定的基础

> 注意：当前 `score` 是工程上的近似分数，不是严格概率分数。

---

### 4.2 SourceItem 增强

位置：`app/schemas.py`

`SourceItem` 现已支持：

- `source`
- `file_type`
- `chunk_index`
- `snippet`
- `score`
- `distance`
- `start_offset`
- `end_offset`
- `title`
- `section`

#### 价值

- 返回信息更完整
- 更利于调试和前端展示
- 为后续高亮定位、跳转原文、展示章节信息打基础

---

### 4.3 新增 retrieval 配置项

位置：`app/config.py`

新增配置：

- `retrieval_fetch_k`
- `retrieval_score_threshold`
- `grounded_top_score_threshold`
- `grounded_average_score_threshold`
- `grounded_min_chunks`
- `max_context_chars`
- `enable_rerank`
- `rerank_top_n`

#### 作用说明

- `retrieval_fetch_k`：初召回数量，允许先多取再筛
- `retrieval_score_threshold`：低质量检索结果过滤阈值
- `grounded_top_score_threshold`：top result 的 grounded 判定阈值
- `grounded_average_score_threshold`：平均分 grounded 判定阈值
- `grounded_min_chunks`：至少需要多少有效 chunk 才认为证据成立
- `max_context_chars`：限制最终送给 prompt 的上下文预算
- `enable_rerank` / `rerank_top_n`：为未来 rerank 预留

---

### 4.4 切块策略升级

位置：`app/services/text_splitter.py`

V1 的切块方式是固定字符窗滑动。V2 改为两级策略：

1. **优先按段落 / 空行切分**
2. **当单段超长时，再退化为带 overlap 的窗口切块**

#### 新增 metadata

每个 chunk 现在会记录：

- `start_offset`
- `end_offset`
- `title`
- `section`

#### 其他改进

- chunk id 使用稳定规则生成，避免重复 ingest 时 id 混乱
- 标题 / section 会尽量从块内首个结构化标题中提取

#### 价值

- 避免过早打断语义单元
- 降低标题与正文被拆散的概率
- 提高检索命中后 snippet 的可读性
- 为后续命中高亮和原文定位提供依据

---

### 4.5 snippet 生成优化

位置：`app/services/retrieval_service.py`

旧逻辑直接截取 `document[:240]`。

新逻辑会：

- 先清理空白字符
- 再生成更自然的单行 snippet
- 超长时使用省略号截断

#### 价值

- 引用更适合接口返回和 UI 展示
- 避免把原始换行和噪音直接塞进 `sources`

---

### 4.6 Retrieval 后处理增强

位置：`app/services/retrieval_service.py`

`retrieve()` 现已拆成更清晰的阶段：

1. 问题向量化
2. 初召回
3. score 过滤
4. 可选 rerank（当前预留）
5. 去重
6. 相邻 chunk 合并
7. 上下文预算裁剪
8. 构造 prompt context
9. 构造 API `sources`

#### 已实现逻辑

##### 低质量过滤
低于 `retrieval_score_threshold` 的结果会被直接丢弃。

##### 去重
相同来源、相同 offset、相同内容的 chunk 不再重复保留。

##### 相邻 chunk 合并
对于同一 `source`、chunk 序号连续且 offset 接近的 chunk，会在入 prompt 前做简单合并。

##### 上下文预算控制
最终进入 prompt 的 chunk 会受 `max_context_chars` 限制，避免简单堆叠 top-k 原文。

#### 价值

- 减少重复内容浪费上下文
- 提升 prompt 中证据块的可读性
- 让上下文长度更稳定
- 让送给模型的上下文更“干净”

---

### 4.7 Prompt 上下文模板升级

位置：`app/core/prompt_builder.py`

当前 prompt 仍通过 `build_qa_prompt()` 统一构造，没有把拼接逻辑散落到 router 或其他 service。

上下文内容现在会尽量保留：

- citation 编号
- `source`
- `file_type`
- `chunk_index`
- `score`
- `offsets`
- `section`
- `content`

#### 价值

- 提高上下文可解释性
- 便于 LLM 优先使用高质量证据
- 便于后续调试回答引用来源

---

### 4.8 grounded 判定替换为检索质量判定

位置：`app/services/retrieval_service.py`

V1 中 grounded 判定依赖问题文本与 snippet 的 token overlap，这种方案：

- 对中文几乎没有价值
- 对同义表达不稳定
- 容易被词面重合误判

V2 中已改为以下优先级：

1. 检查 top result score 是否达标
2. 检查平均 score 是否达标
3. 检查过滤后有效 chunk 数是否足够

当证据不足时，`/qa` 会稳定返回：

`根据当前文档无法确定。`

#### 价值

- grounded 判定更符合语义检索链路
- 对同义问题更稳
- 对词面重合但无答案的问题更保守

---

### 4.9 `/qa` 路由行为调整

位置：`app/routers/qa.py`

当前逻辑：

1. 从请求或默认配置中得到 `top_k`
2. 调用 `RetrievalService.retrieve()` 得到 `context + sources`
3. 若向量库为空，则返回 `400`
4. 若 grounded 判定失败，则返回 `根据当前文档无法确定。`
5. 否则构造 prompt 并调用 `LLMService`

#### 变化点

- “没有已索引内容”和“有索引但当前问题证据不足”被清晰区分
- grounded 判断不再依赖 token overlap

---

### 4.10 rerank 预留但未启用

位置：`app/config.py`、`app/services/retrieval_service.py`

本轮已经预留：

- `enable_rerank`
- `rerank_top_n`

同时 `RetrievalService` 内部结构已经允许未来演进成：

`初召回 -> 可选 rerank -> 最终上下文组装`

#### 为什么暂缓

- 当前系统仍处于基础检索能力增强阶段
- 先把 metadata、chunk、过滤、合并、grounded 做扎实，通常收益更高
- 暂不引入新依赖，避免本轮复杂度上升过快

---

## 5. 接口变化

### `/qa` 返回的 `sources` 更丰富

示例：

```json
{
  "answer": "The system supports POST /qa for question answering.",
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

### 保持兼容的部分

- `/ingest` 接口路径未变
- `/qa` 接口路径未变
- `QAResponse` 顶层结构仍是：
  - `answer`
  - `grounded`
  - `sources`

---

## 6. 已完成测试覆盖

### `tests/test_splitter.py`
覆盖：

- 段落优先切分
- 超长段落降级切分
- `start_offset` / `end_offset`
- 稳定 chunk id

### `tests/test_retrieval_service.py`
覆盖：

- 分数过滤
- 相邻 chunk 合并
- 上下文预算裁剪
- grounded 判定
- score/source metadata 构造

### `tests/test_qa.py`
覆盖：

- 没有已索引内容返回 `400`
- 证据不足时返回 `根据当前文档无法确定。`
- grounded 回答时返回更丰富的 sources
- 未传 `top_k` 时回退默认值

### `tests/test_ingest.py`
回归验证：

- 正常 ingest
- 无文档时报错
- 目录缺失时报错

---

## 7. 本地验证结果

本次使用以下命令完成针对性验证：

```bash
python -m pytest "D:/python/Codebase QA Copilot/tests/test_splitter.py" "D:/python/Codebase QA Copilot/tests/test_retrieval_service.py" "D:/python/Codebase QA Copilot/tests/test_qa.py" "D:/python/Codebase QA Copilot/tests/test_ingest.py"
```

结果：

- `17 passed`

---

## 8. 当前已知限制

虽然 Retrieval V2 已显著优于 V1，但仍有一些已知限制：

1. 当前 `score` 是基于 `1 - distance` 的近似映射，不是标准化语义分数
2. rerank 仍是预留结构，未引入真实 reranker
3. snippet 目前仍是基于 chunk 内容本身生成，尚未实现“命中附近片段”截取
4. merge 策略是轻量规则法，尚未做更复杂的语义合并
5. 上下文预算使用字符数近似，而不是 token 精算

---

## 9. 本轮明确暂缓的内容

以下内容不在本次 V2 范围内：

- 多向量库或多检索后端抽象
- query rewrite / agentic retrieval
- 前端级文档管理系统
- 重型 observability 平台接入
- 真正的 reranker 依赖接入

---

## 10. 建议的后续演进方向

### V2.1

- 增强 snippet，优先截取命中附近片段
- 调整 score 阈值默认值，基于真实样本做校准
- 增加更多端到端样例验证

### V2.5

- 接入真实 reranker
- 将 context budget 从字符数近似升级为 token 预算
- 增加更强的 chunk merge / section-aware grouping

### 更后续阶段

- 混合检索（语义 + lexical）
- 查询改写
- 更强的引用落点定位能力
- UI 层展示原文高亮与 source drill-down

---

## 11. 总结

本次 Retrieval V2 没有改变系统主干结构，而是在现有架构上有针对性地增强了检索质量：

- 检索结果更可判断
- chunk 更自然
- 上下文更干净
- 引用更完整
- grounded 更可靠

相较 V1，这一版更接近“可用于真实问答验证”的 RAG 基线，也为后续 rerank 和更高阶检索能力提供了更稳的基础。
