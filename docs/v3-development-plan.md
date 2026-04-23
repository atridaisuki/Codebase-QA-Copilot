# V3 开发计划：工程化 + 检索增强 + 评估体系

> 目标：把项目从"能跑的 MVP"升级为"工程化完整、检索有深度、效果可量化"的状态，简历上能站住脚。

---

## 总览

分两条线并行推进，共 5 个阶段：

```
工程化线：  Phase 1 ──→ Phase 2 ──────────────────────→ Phase 5（收尾）
检索增强线：            Phase 3 ──→ Phase 4 ──────────→ Phase 5（收尾）
```

- Phase 1：工程化基础设施（代码质量工具链 + CI/CD）
- Phase 2：Docker 增强 + 部署就绪
- Phase 3：多路召回（BM25 + 向量融合）
- Phase 4：Reranker 接入
- Phase 5：评估体系 + 收尾打磨

---

## Phase 1：工程化基础设施

> 目标：让项目有现代 Python 项目该有的样子。

### 1.1 迁移到 pyproject.toml

把 `requirements.txt` 迁移到 `pyproject.toml`，用 `[project.optional-dependencies]` 管理开发依赖。

```toml
[project]
name = "codebase-qa-copilot"
version = "0.3.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.116.0",
    "uvicorn[standard]>=0.35.0",
    "pydantic>=2.11.0",
    "pydantic-settings>=2.10.0",
    "chromadb>=1.0.0",
    "sentence-transformers>=5.0.0",
    "anthropic>=0.62.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.4.0",
    "pytest-cov>=6.0",
    "httpx>=0.28.0",
    "ruff>=0.11.0",
    "mypy>=1.15.0",
    "pre-commit>=4.0.0",
]
```

保留 `requirements.txt` 给 Dockerfile 用（`pip install -r` 比 `pip install .` 在 Docker 缓存上更友好），但内容从 pyproject.toml 生成。

### 1.2 Ruff（lint + format）

新增 `ruff` 配置到 `pyproject.toml`：

```toml
[tool.ruff]
target-version = "py311"
line-length = 120

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
]
ignore = ["E501"]  # line length 交给 formatter
```

### 1.3 Mypy（类型检查）

```toml
[tool.mypy]
python_version = "3.11"
strict = false
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

目标不是 strict mode 全开，而是确保所有函数都有类型标注、没有明显的类型错误。

### 1.4 Pre-commit hooks

新增 `.pre-commit-config.yaml`：

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.15.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, fastapi]
```

### 1.5 pytest-cov（测试覆盖率）

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=app --cov-report=term-missing --cov-report=html"
```

目标覆盖率：核心 service 层 ≥ 80%。

### 1.6 Makefile

```makefile
.PHONY: install lint format typecheck test run

install:
	pip install -e ".[dev]"

lint:
	ruff check app tests

format:
	ruff format app tests

typecheck:
	mypy app

test:
	pytest

run:
	uvicorn app.main:app --reload
```

### 1.7 GitHub Actions CI

新增 `.github/workflows/ci.yml`：

```yaml
name: CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: ruff check app tests
      - run: ruff format --check app tests
      - run: mypy app
      - run: pytest --cov=app --cov-fail-under=70
```

### 1.8 涉及的文件变更

| 操作 | 文件 |
|------|------|
| 新增 | `pyproject.toml` |
| 新增 | `.pre-commit-config.yaml` |
| 新增 | `Makefile` |
| 新增 | `.github/workflows/ci.yml` |
| 修改 | `requirements.txt`（从 pyproject.toml 生成，保留给 Docker） |
| 修改 | 现有代码（修复 ruff/mypy 报出的问题） |

---

## Phase 2：Docker 增强 + 部署就绪

> 目标：Dockerfile 达到生产级标准，一键 docker-compose up 能跑。

### 2.1 Dockerfile 优化

当前问题：
- 用 root 用户运行
- 没有 healthcheck
- 没有多阶段构建
- COPY 了不必要的文件

优化后的结构：

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
# 非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app ./app
# 数据目录由 volume 挂载，不 COPY 进镜像
RUN mkdir -p data/docs data/chroma && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

关键改进：
- 多阶段构建：builder 阶段装依赖，最终镜像更小
- 非 root 用户运行
- HEALTHCHECK 指令
- 数据目录通过 volume 挂载，不打进镜像

### 2.2 docker-compose.yml

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./data/docs:/app/data/docs:ro
      - chroma_data:/app/data/chroma
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 5s
      retries: 3

volumes:
  chroma_data:
```

### 2.3 .dockerignore

```
.git
.venv
__pycache__
*.pyc
.env
data/chroma
.github
docs
tests
*.md
```

### 2.4 .env.example 完善

确保所有配置项都有注释说明和合理默认值。

### 2.5 涉及的文件变更

| 操作 | 文件 |
|------|------|
| 修改 | `Dockerfile` |
| 新增 | `docker-compose.yml` |
| 新增 | `.dockerignore` |
| 修改 | `.env.example` |

---

## Phase 3：多路召回（BM25 + 向量检索融合）

> 目标：从单一向量检索升级为向量 + 关键词双路召回，用 RRF 融合排序。

### 3.1 为什么要做

当前只有向量检索（语义匹配），存在明显短板：
- 精确关键词匹配弱（用户搜 "BM25" 这个词，语义检索可能找不到最相关的段落）
- 对专有名词、代码片段、配置项等"字面匹配"场景效果差
- 工业界 RAG 标配是混合检索，面试时只有向量检索会被追问

### 3.2 技术方案

#### 新增 BM25 检索器

新增 `app/services/bm25_service.py`：

```python
class BM25Service:
    """基于 rank-bm25 的关键词检索服务"""

    def __init__(self):
        self.tokenizer = ...  # jieba 分词（中文）或空格分词（英文）
        self.bm25 = None
        self.corpus_chunks = []

    def index(self, chunks: list[ChunkData]) -> None:
        """构建 BM25 索引"""
        ...

    def search(self, query: str, top_k: int) -> list[BM25Result]:
        """关键词检索，返回 chunk + BM25 分数"""
        ...
```

依赖：`rank-bm25`（纯 Python，无重依赖）+ `jieba`（中文分词）。

#### BM25 索引持久化

BM25 索引在 `/ingest` 时构建，序列化到 `data/bm25_index.pkl`。服务启动时自动加载。

#### RRF 融合（Reciprocal Rank Fusion）

在 `RetrievalService` 中新增融合逻辑：

```python
def _rrf_merge(
    self,
    vector_results: list[RetrievedChunk],
    bm25_results: list[BM25Result],
    k: int = 60,
) -> list[RetrievedChunk]:
    """
    RRF 公式：score(d) = Σ 1 / (k + rank_i(d))
    k=60 是论文推荐的默认值
    """
    ...
```

RRF 的好处：不需要对两路分数做归一化，直接用排名融合，简单且效果稳定。

#### 检索流程变更

```
用户提问
  ↓
┌─────────────────┬──────────────────┐
│ 向量检索（现有）   │ BM25 关键词检索    │
│ top_k=fetch_k   │ top_k=fetch_k    │
└────────┬────────┴────────┬─────────┘
         │                 │
         └────────┬────────┘
                  ↓
          RRF 融合排序
                  ↓
          后续流程不变（过滤→去重→合并→预算控制）
```

### 3.3 配置项新增

```python
# config.py 新增
enable_hybrid_search: bool = Field(default=True)
bm25_weight: float = Field(default=1.0)       # RRF 中 BM25 路的权重
vector_weight: float = Field(default=1.0)      # RRF 中向量路的权重
bm25_index_path: str = Field(default="data/bm25_index.pkl")
```

### 3.4 涉及的文件变更

| 操作 | 文件 |
|------|------|
| 新增 | `app/services/bm25_service.py` |
| 修改 | `app/services/retrieval_service.py`（加入 RRF 融合） |
| 修改 | `app/routers/ingest.py`（ingest 时同步构建 BM25 索引） |
| 修改 | `app/config.py`（新增配置项） |
| 新增 | `tests/test_bm25_service.py` |
| 修改 | `tests/test_retrieval_service.py`（覆盖融合逻辑） |
| 修改 | `pyproject.toml`（新增 rank-bm25、jieba 依赖） |

### 3.5 面试怎么讲

> "我们的检索用的是混合召回：向量检索负责语义匹配，BM25 负责精确关键词匹配，两路结果通过 RRF 融合排序。这样既能处理'Docker 是什么'这种语义问题，也能处理'HNSW 参数配置'这种精确查找。RRF 的好处是不需要对两路分数做归一化，直接用排名融合，实现简单且效果稳定。"

---

## Phase 4：Reranker 接入

> 目标：在初步召回后用 cross-encoder 重排序，提升最终送入 LLM 的上下文质量。

### 4.1 为什么要做

当前的排序完全依赖初召回的分数（向量距离 or RRF 分数），这些分数是"粗排"。cross-encoder reranker 会同时看 query 和 document，做更精确的相关性判断。

类比搜索引擎：
- 向量检索 / BM25 = 召回阶段（快但粗）
- Reranker = 精排阶段（慢但准）

### 4.2 技术方案

#### 新增 Reranker 服务

新增 `app/services/reranker_service.py`：

```python
from sentence_transformers import CrossEncoder

class RerankerService:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        top_n: int,
    ) -> list[RetrievedChunk]:
        """用 cross-encoder 对 query-chunk 对打分，重排序后返回 top_n"""
        pairs = [(query, chunk.content) for chunk in chunks]
        scores = self.model.predict(pairs)
        # 按 rerank 分数重排，更新 chunk.score
        ...
```

模型选择：`cross-encoder/ms-marco-MiniLM-L-6-v2`
- 体积小（~80MB），CPU 可跑
- 英文效果好；中文场景可换 `BAAI/bge-reranker-base`
- sentence-transformers 已经是现有依赖，不需要额外装包

#### 集成到检索流程

修改 `RetrievalService._apply_rerank()`，把现在的空壳实现替换为真实调用：

```python
def _apply_rerank(self, chunks: list[RetrievedChunk], question: str) -> list[RetrievedChunk]:
    if not chunks or not self.settings.enable_rerank:
        return chunks
    return self.reranker.rerank(question, chunks, top_n=self.settings.rerank_top_n)
```

#### 检索流程（完整版）

```
用户提问
  ↓
向量检索 + BM25 → RRF 融合（Phase 3）
  ↓
score 过滤
  ↓
Reranker 精排（Phase 4，本阶段）
  ↓
去重 → 合并 → 预算控制
  ↓
Grounding 判定 → LLM 生成
```

### 4.3 配置项调整

```python
# config.py 修改
enable_rerank: bool = Field(default=True)  # 改为默认开启
rerank_top_n: int = Field(default=3)
rerank_model_name: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")
```

### 4.4 性能考量

- Reranker 是 CPU 密集型操作，对每个 query-chunk 对都要跑一次模型推理
- 控制输入 reranker 的 chunk 数量（建议 ≤ 20），不要把所有初召回结果都丢进去
- 首次加载模型有冷启动时间（~2-3s），之后每次 rerank 约 50-200ms（取决于 chunk 数量和长度）
- 可以考虑在 `main.py` 启动时预加载模型

### 4.5 涉及的文件变更

| 操作 | 文件 |
|------|------|
| 新增 | `app/services/reranker_service.py` |
| 修改 | `app/services/retrieval_service.py`（替换 `_apply_rerank` 空壳） |
| 修改 | `app/config.py`（新增 rerank_model_name，enable_rerank 改默认值） |
| 新增 | `tests/test_reranker_service.py` |
| 修改 | `tests/test_retrieval_service.py`（覆盖 rerank 集成） |

### 4.6 面试怎么讲

> "初召回后我加了一个 cross-encoder reranker 做精排。bi-encoder（向量检索）的优势是快，它把 query 和 document 分别编码再算相似度；cross-encoder 的优势是准，它把 query 和 document 拼在一起过模型，能捕捉更细粒度的交互。代价是慢，所以只对初召回的 top-20 做 rerank，最终取 top-3 送入 LLM。"

---

## Phase 5：评估体系 + 收尾

> 目标：用数据证明你的优化有效果，而不是"我觉得效果还行"。

### 5.1 构造评估数据集

新增 `eval/` 目录：

```
eval/
├── dataset.json          # 评估数据集
├── run_eval.py           # 评估脚本
└── results/              # 评估结果输出
```

`dataset.json` 格式：

```json
[
  {
    "question": "Docker 和虚拟机有什么区别？",
    "expected_sources": ["data/docs/docker.md"],
    "expected_keywords": ["容器", "内核", "隔离"],
    "difficulty": "easy"
  },
  {
    "question": "如何优化 Dockerfile 的构建速度？",
    "expected_sources": ["data/docs/docker.md"],
    "expected_keywords": ["分层", "缓存", "multi-stage"],
    "difficulty": "medium"
  }
]
```

手动构造 20-30 条，覆盖：
- 简单事实问题（答案在单个 chunk 里）
- 跨段落问题（需要多个 chunk 拼接）
- 精确关键词问题（测试 BM25 的价值）
- 无答案问题（测试 grounding 判定）

### 5.2 评估指标

#### 检索质量指标

```python
# eval/run_eval.py

def evaluate_retrieval(dataset, retrieval_service):
    metrics = {
        "recall@3": ...,    # top-3 结果中包含正确来源的比例
        "recall@5": ...,    # top-5
        "mrr": ...,         # Mean Reciprocal Rank，正确来源首次出现的排名倒数的均值
        "precision@3": ..., # top-3 中相关结果的比例
    }
    return metrics
```

核心指标解释：
- **Recall@K**：在返回的 top-K 结果中，有多少比例包含了正确答案的来源文件。越高越好。
- **MRR**：正确来源第一次出现在第几位？如果第 1 位就命中，得分 1.0；第 2 位命中得分 0.5；第 3 位得分 0.33。
- **Precision@K**：top-K 结果中有多少是真正相关的（而不是凑数的噪音）。

#### 生成质量指标（轻量版）

不搞复杂的 LLM-as-judge，用简单可靠的方式：
- **关键词命中率**：回答中是否包含 expected_keywords
- **Grounding 准确率**：有答案的问题 grounded=true，无答案的问题 grounded=false
- **来源引用准确率**：回答引用的来源是否和 expected_sources 匹配

### 5.3 对比实验

评估脚本支持对比不同配置的效果：

```python
configs = [
    {"name": "vector_only",  "enable_hybrid_search": False, "enable_rerank": False},
    {"name": "hybrid",       "enable_hybrid_search": True,  "enable_rerank": False},
    {"name": "hybrid+rerank","enable_hybrid_search": True,  "enable_rerank": True},
]

for config in configs:
    results = run_evaluation(dataset, config)
    print(f"{config['name']}: Recall@3={results['recall@3']:.2f}, MRR={results['mrr']:.2f}")
```

预期输出类似：

```
vector_only:    Recall@3=0.65, MRR=0.58, Precision@3=0.52
hybrid:         Recall@3=0.78, MRR=0.71, Precision@3=0.63
hybrid+rerank:  Recall@3=0.82, MRR=0.79, Precision@3=0.74
```

这组数据就是你面试时的"硬通货"。

### 5.4 README 完善

更新 README.md，包含：
- 项目简介和架构图
- 技术栈说明
- 快速启动（docker-compose up）
- API 文档链接
- 检索流程图
- 评估结果摘要
- 项目结构说明

### 5.5 涉及的文件变更

| 操作 | 文件 |
|------|------|
| 新增 | `eval/dataset.json` |
| 新增 | `eval/run_eval.py` |
| 新增 | `eval/results/`（.gitkeep） |
| 修改 | `README.md` |
| 修改 | 各模块补充类型标注（mypy 要求） |

---

## 最终项目结构

```
codebase-qa-copilot/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── core/
│   │   ├── error_handlers.py
│   │   ├── logging.py
│   │   └── prompt_builder.py
│   ├── routers/
│   │   ├── health.py
│   │   ├── ingest.py
│   │   └── qa.py
│   ├── services/
│   │   ├── bm25_service.py          ← 新增
│   │   ├── document_loader.py
│   │   ├── embedding_service.py
│   │   ├── llm_service.py
│   │   ├── reranker_service.py       ← 新增
│   │   ├── retrieval_service.py      ← 重点修改
│   │   ├── text_splitter.py
│   │   └── vector_store.py
│   ├── config.py
│   ├── main.py
│   └── schemas.py
├── data/
│   ├── docs/
│   └── chroma/
├── eval/                              ← 新增
│   ├── dataset.json
│   ├── run_eval.py
│   └── results/
├── tests/
│   ├── test_bm25_service.py          ← 新增
│   ├── test_health.py
│   ├── test_ingest.py
│   ├── test_loader.py
│   ├── test_qa.py
│   ├── test_reranker_service.py      ← 新增
│   ├── test_retrieval_service.py
│   └── test_splitter.py
├── docs/
├── .dockerignore                      ← 新增
├── .pre-commit-config.yaml            ← 新增
├── docker-compose.yml                 ← 新增
├── Dockerfile                         ← 修改
├── Makefile                           ← 新增
├── pyproject.toml                     ← 新增
├── requirements.txt                   ← 保留（Docker 用）
├── .env.example
└── README.md
```

---

## 新增依赖汇总

| 包 | 用途 | 阶段 |
|----|------|------|
| `ruff` | Lint + Format | Phase 1（dev） |
| `mypy` | 类型检查 | Phase 1（dev） |
| `pre-commit` | Git hooks | Phase 1（dev） |
| `pytest-cov` | 测试覆盖率 | Phase 1（dev） |
| `rank-bm25` | BM25 检索 | Phase 3 |
| `jieba` | 中文分词 | Phase 3 |

注意：reranker 用的 `CrossEncoder` 已包含在 `sentence-transformers` 中，不需要额外依赖。

---

## 建议的执行顺序和时间参考

| 阶段 | 内容 | 复杂度 |
|------|------|--------|
| Phase 1 | 工程化基础设施 | 低，主要是配置文件 + 修 lint 问题 |
| Phase 2 | Docker 增强 | 低，改 Dockerfile + 写 compose |
| Phase 3 | 多路召回 | 中，核心是 BM25Service + RRF 融合逻辑 |
| Phase 4 | Reranker | 低-中，框架已预留，填充实现即可 |
| Phase 5 | 评估体系 | 中，构造数据集 + 写评估脚本 + 跑实验 |

Phase 1-2 可以一起做，Phase 3-4 按顺序来（reranker 依赖多路召回的结果），Phase 5 最后收尾。

---

## 面试时的完整故事线

> "这个项目是一个文档问答系统，核心是 RAG 架构。我没有用 LangChain，而是手写了整个检索和生成流程。
>
> 检索层做了三件事：第一是混合召回，向量检索负责语义匹配，BM25 负责精确关键词匹配，两路通过 RRF 融合；第二是 cross-encoder reranker 精排，提升最终上下文的相关性；第三是后处理，包括去重、相邻 chunk 合并、上下文预算控制。
>
> 我还建了一套评估体系，用 Recall@K、MRR 等指标量化检索效果。实验数据显示，混合召回比纯向量检索 Recall@3 提升了约 XX 个百分点，加上 reranker 后又提升了 XX 个百分点。
>
> 工程化方面，项目有完整的 CI/CD（GitHub Actions 跑 lint、类型检查、测试）、Docker 多阶段构建、pre-commit hooks、测试覆盖率 XX%。"
