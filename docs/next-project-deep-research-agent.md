# 下一个项目：Deep Research Agent（深度研究助手）

## 项目背景

前置项目 "Codebase QA Copilot" 已完成，掌握了：
- 完整 RAG pipeline（chunking → embedding → hybrid search → reranking → grounding）
- 基础 Agent（ReAct loop + tool use，3 个工具但协作不足）
- 中文 NLP（jieba + BGE-base-zh）
- FastAPI + SSE streaming
- Claude API 调用（含 extended thinking、tool use）

当前项目的不足：3 个 tool（knowledge_search、list_documents、get_document_outline）本质都是"查文档"的变体，没有真正的多工具协作和任务规划能力。

---

## 项目目标

用户输入一个研究问题，系统自动：
1. 分解问题为子任务
2. 针对每个子任务选择合适的信息源搜索
3. 对搜索结果做摘要和事实核查
4. 整合所有子任务结果，生成结构化研究报告（带引用来源）

## 技术栈

```
编排层:     LlamaIndex Workflows（事件驱动 DAG，比手写 ReAct 更结构化）
LLM:        Claude API（已熟悉）
Web搜索:    Tavily API（免费额度够学习用）
本地知识库: 复用 hybrid search 经验（Chroma + BM25 + RRF）
向量库:     可以试 Qdrant 替代 Chroma（学个新的）
前端:       Streamlit（快速出 demo，不花时间在前端）
可观测性:   LangFuse 或 Arize Phoenix（追踪 agent 执行链路）
输出格式:   Pydantic structured output
```

## 模块拆分

### 模块 1 - Query Planner（查询规划器）
- 输入: 用户的研究问题
- 输出: 子问题列表 + 每个子问题的搜索策略（web/local/arxiv）
- 实现: LLM structured output，用 Pydantic model 定义输出格式
- 学习重点: 让 LLM 做 planning 而不是直接回答

```python
# 示例输出结构
class SubQuery(BaseModel):
    question: str
    search_strategy: Literal["web", "local_kb", "arxiv"]
    priority: int

class QueryPlan(BaseModel):
    original_question: str
    sub_queries: list[SubQuery]
    expected_report_structure: list[str]  # 报告大纲
```

### 模块 2 - Multi-Source Retriever（多源检索器）
- 信息源:
  - Web Search: Tavily API
  - Local Knowledge Base: 复用 hybrid search（向量 + BM25 + RRF）
  - 可选: Arxiv API / Wikipedia API
- 学习重点: 不同子问题路由到不同信息源，工具之间真正需要协作

### 模块 3 - Summarizer & Fact Checker（摘要 + 事实核查）
- 对每个子任务的检索结果做:
  - 摘要提取（map-reduce 或 refine 模式）
  - 信息冲突检测（不同来源说法矛盾时标注）
- 学习重点: 多轮 LLM 调用的编排，context window 管理

### 模块 4 - Report Generator（报告生成器）
- 整合所有子任务结果，生成:
  - 结构化 Markdown 报告
  - 带引用来源的段落（[1] [2] 标注）
  - 置信度标注（高/中/低）
- 学习重点: 长文本生成的 prompt 工程

### 模块 5 - Orchestrator（编排层）★ 核心
- 用 LlamaIndex Workflow 把上面串起来:
  - 定义 step 之间的依赖关系（DAG）
  - 子任务并行执行
  - 失败重试 + 超时处理
  - 中间状态可持久化
- 学习重点: 真正的 agent 编排，这是整个项目最重要的部分

### 模块 6 - Observability（可观测性）
- 接入 LangFuse 或 Phoenix:
  - 追踪每次 LLM 调用的 input/output/latency/cost
  - 可视化 agent 执行链路（哪个 step 花了多久，哪里失败了）
- 学习重点: 生产级 AI 应用必备能力，越早接入越好

## 建议实现顺序

```
第 1 步: 过 LlamaIndex Workflows 文档和示例（1-2 天）
第 2 步: 模块 1 + 2 → 跑通"分解问题 → 搜索 → 返回结果"
第 3 步: 模块 6 → 尽早接入可观测性，后续调试全靠它
第 4 步: 模块 3 → 加摘要能力
第 5 步: 模块 4 + 5 → 完整编排 + 报告生成
```

## 相比当前项目的进阶点

| 当前项目 (Codebase QA) | 新项目 (Deep Research) |
|------------------------|----------------------|
| 单轮问答 | 多步推理 |
| 单一信息源（本地文档） | 多源检索 + 路由 |
| ReAct while 循环 | DAG 编排 (Workflow) |
| 工具各自独立 | 工具结果互相依赖 |
| 无执行追踪 | 完整可观测性 |
| 返回答案文本 | 生成结构化报告 |
| 无 planning | LLM 做查询规划 |

## 关于框架选择

手写 vs 框架的原则：**学原理时手写，做工程时用框架**。

- 底层能力（检索、embedding、chunking）→ 继续手写，从当前项目搬过去
- 编排层（多步骤协调、并行、状态管理）→ 用 LlamaIndex Workflows
- LLM 调用 → 直接调 Claude API，你已经会了

LlamaIndex Workflows 的核心概念很简单：
- `Step`: 一个处理步骤（函数）
- `Event`: 步骤之间传递的数据
- `Workflow`: 把多个 Step 串成 DAG
- 框架自动处理并发、重试、状态管理

建议第一步先纯手写一个最简版（不用框架），跑通后再用 Workflows 重构，这样能理解框架到底帮你省了什么。
