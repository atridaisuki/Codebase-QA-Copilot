# Python Web + AI 应用：数据库面试知识点详解

## 一、关系型数据库基础（MySQL / PostgreSQL）

### 1.1 为什么 Web + AI 项目离不开关系型数据库

AI 应用的核心数据（用户、权限、任务记录、计费）仍然需要强一致性和事务保证，关系型数据库是最成熟的选择。

典型场景：
- 用户系统、RBAC 权限管理
- AI 对话历史、Prompt 模板管理
- 异步任务状态追踪（Celery task results）
- 向量检索的元数据存储（配合向量数据库使用）

### 1.2 MySQL vs PostgreSQL 选型

| 维度 | MySQL | PostgreSQL |
|------|-------|-----------|
| JSON 支持 | 5.7+ 支持 JSON 类型 | 原生 JSONB，索引更强 |
| 向量扩展 | 无原生支持 | pgvector 扩展，可直接做向量检索 |
| 全文检索 | 基础支持 | 内置 tsvector，支持中文分词插件 |
| 并发模型 | 基于锁 | MVCC 更成熟 |
| Python 生态 | SQLAlchemy / Django ORM 完美支持 | 同左，且 asyncpg 性能极强 |
| AI 场景推荐 | 中小项目、团队熟悉 MySQL | **推荐**：pgvector 一站式解决元数据+向量 |

> **面试高频问题**：为什么你的 AI 项目选了 PostgreSQL？
> 回答思路：pgvector 扩展让我们不需要额外部署向量数据库，降低运维复杂度；JSONB 方便存储非结构化的 LLM 响应；asyncpg 配合 FastAPI 异步架构性能优秀。

---

## 二、SQL 核心知识

### 2.1 索引原理与优化

**B+ 树索引（InnoDB 默认）：**
- 叶子节点存储数据，非叶子节点只存键值
- 所有叶子节点通过双向链表连接，支持范围查询
- 树高度通常 3-4 层，千万级数据也只需 3-4 次磁盘 IO

**面试常考索引问题：**

```sql
-- 联合索引最左前缀原则
CREATE INDEX idx_user ON conversations(user_id, created_at, status);

-- 能用到索引
SELECT * FROM conversations WHERE user_id = 1;
SELECT * FROM conversations WHERE user_id = 1 AND created_at > '2024-01-01';

-- 不能用到索引（跳过了 user_id）
SELECT * FROM conversations WHERE created_at > '2024-01-01';
SELECT * FROM conversations WHERE status = 'active';
```

**覆盖索引：**
```sql
-- 查询的字段全部在索引中，无需回表
SELECT user_id, created_at FROM conversations
WHERE user_id = 1 AND created_at > '2024-01-01';
```

### 2.2 事务与隔离级别

四大隔离级别（从低到高）：

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|---------|------|-----------|------|------|
| READ UNCOMMITTED | 可能 | 可能 | 可能 | 最高 |
| READ COMMITTED | 不可能 | 可能 | 可能 | 高 |
| REPEATABLE READ（MySQL 默认） | 不可能 | 不可能 | InnoDB 通过间隙锁解决 | 中 |
| SERIALIZABLE | 不可能 | 不可能 | 不可能 | 最低 |

**AI 应用中的事务场景：**
```python
# FastAPI + SQLAlchemy 异步事务示例
async def create_conversation_with_message(db: AsyncSession, user_id: int, content: str):
    async with db.begin():
        conv = Conversation(user_id=user_id)
        db.add(conv)
        await db.flush()  # 获取 conv.id
        msg = Message(conversation_id=conv.id, content=content, role="user")
        db.add(msg)
    # 离开 begin() 自动 commit，异常自动 rollback
```

### 2.3 慢查询分析

```sql
-- MySQL 开启慢查询日志
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;  -- 超过 1 秒记录

-- EXPLAIN 分析执行计划
EXPLAIN SELECT * FROM documents WHERE embedding_status = 'pending'
ORDER BY created_at LIMIT 100;
```

EXPLAIN 关键字段：
- `type`：ALL（全表扫描）→ index → range → ref → const，越往右越好
- `key`：实际使用的索引
- `rows`：预估扫描行数
- `Extra`：Using filesort / Using temporary 需要优化

---

## 三、ORM 与数据库迁移

### 3.1 SQLAlchemy（Python Web + AI 首选 ORM）

**模型定义：**
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, JSON
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(default="New Chat")
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    messages: Mapped[list["Message"]] = relationship(back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str]  # "user" | "assistant" | "system"
    content: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int | None]
    model: Mapped[str | None]  # "gpt-4" / "claude-3"

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
```

**面试常问：N+1 查询问题**
```python
# 错误：N+1 查询（1 次查 conversations + N 次查 messages）
convs = await db.execute(select(Conversation).where(...))
for conv in convs.scalars():
    print(conv.messages)  # 每次触发一条 SQL

# 正确：joinedload 一次性加载
from sqlalchemy.orm import joinedload
stmt = select(Conversation).options(joinedload(Conversation.messages)).where(...)
convs = await db.execute(stmt)
```

### 3.2 Alembic 数据库迁移

```bash
# 初始化
alembic init alembic

# 自动生成迁移脚本
alembic revision --autogenerate -m "add token_count to messages"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

> **面试考点**：生产环境如何安全做数据库迁移？
> 回答：分阶段迁移（先加列再改代码再删旧列）、避免锁表的 DDL（`ALTER TABLE ... ALGORITHM=INPLACE`）、蓝绿部署配合迁移脚本、迁移前备份。

---

## 四、向量数据库（AI 应用核心）

### 4.1 为什么需要向量数据库

传统数据库基于精确匹配（`WHERE name = 'xxx'`），而 AI 应用需要**语义相似度检索**：
- RAG（检索增强生成）：把用户问题转为向量，检索最相关的文档片段
- 推荐系统：基于 embedding 相似度推荐
- 图片/音频检索：多模态 embedding 检索

### 4.2 主流向量数据库对比

| 数据库 | 类型 | 适用场景 | Python 集成 |
|--------|------|---------|------------|
| pgvector | PG 扩展 | 中小规模，已有 PG 基础设施 | SQLAlchemy + pgvector |
| ChromaDB | 嵌入式 | 原型开发、本地测试 | `import chromadb` |
| Milvus | 分布式 | 大规模生产环境（亿级向量） | pymilvus |
| Pinecone | 云托管 | 不想运维、快速上线 | pinecone-client |
| Qdrant | 独立部署 | 中大规模，过滤性能好 | qdrant-client |
| FAISS | 库（非数据库） | 纯内存检索、研究场景 | faiss-cpu / faiss-gpu |

### 4.3 向量检索核心概念

**Embedding 维度：**
- OpenAI text-embedding-3-small：1536 维
- BGE-large-zh：1024 维
- 维度越高表达能力越强，但存储和检索成本也越高

**相似度度量：**
```python
# 余弦相似度（最常用，归一化后等价于内积）
cosine_similarity = dot(a, b) / (norm(a) * norm(b))

# L2 距离（欧氏距离）
l2_distance = sqrt(sum((a - b) ** 2))

# 内积（向量已归一化时等价于余弦相似度）
inner_product = dot(a, b)
```

**索引类型：**
- FLAT：暴力搜索，100% 精确，小数据集用
- IVF（Inverted File）：聚类后只搜索最近的几个簇，适合百万级
- HNSW（Hierarchical Navigable Small World）：图索引，查询快但内存占用大，**最常用**
- PQ（Product Quantization）：压缩向量，牺牲精度换空间

### 4.4 pgvector 实战（面试加分项）

```sql
-- 安装扩展
CREATE EXTENSION vector;

-- 创建表
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI embedding 维度
    document_id INT REFERENCES documents(id),
    metadata JSONB DEFAULT '{}'
);

-- 创建 HNSW 索引（推荐）
CREATE INDEX ON document_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);

-- 语义检索：找最相似的 5 个片段
SELECT id, content, 1 - (embedding <=> $1::vector) AS similarity
FROM document_chunks
WHERE document_id = ANY($2)
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

**SQLAlchemy + pgvector：**
```python
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, Text

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))

# 检索
from sqlalchemy import text
results = await db.execute(
    select(DocumentChunk)
    .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
    .limit(5)
)
```

---

## 五、数据库连接池与异步

### 5.1 为什么需要连接池

数据库连接的创建和销毁开销大（TCP 握手 + 认证），连接池复用已有连接。

```python
# SQLAlchemy 异步连接池配置
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/dbname",
    pool_size=20,          # 常驻连接数
    max_overflow=10,       # 允许额外创建的连接数（峰值 30）
    pool_timeout=30,       # 获取连接的超时时间
    pool_recycle=3600,     # 连接最大存活时间（避免被数据库断开）
    pool_pre_ping=True,    # 使用前检测连接是否存活
)
```

> **面试问题**：pool_size 设多大合适？
> 回答：取决于数据库最大连接数和应用实例数。PostgreSQL 默认 max_connections=100，如果有 4 个 worker 进程，每个 pool_size=20 刚好用满。可以用 PgBouncer 做连接池中间件进一步优化。

### 5.2 FastAPI 中的数据库会话管理

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 依赖注入
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@app.post("/conversations")
async def create_conversation(db: AsyncSession = Depends(get_db)):
    # db 在请求结束后自动归还连接池
    ...
```

---

## 六、缓存策略（Redis + 数据库）

### 6.1 常见缓存模式

**Cache-Aside（旁路缓存，最常用）：**
```python
async def get_user_config(user_id: int, redis: Redis, db: AsyncSession):
    # 1. 先查缓存
    cache_key = f"user_config:{user_id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. 缓存未命中，查数据库
    result = await db.execute(select(UserConfig).where(UserConfig.user_id == user_id))
    config = result.scalar_one_or_none()
    if config:
        # 3. 写入缓存（设置过期时间）
        await redis.setex(cache_key, 3600, json.dumps(config.to_dict()))
    return config
```

**缓存三大问题：**

| 问题 | 描述 | 解决方案 |
|------|------|---------|
| 缓存穿透 | 查询不存在的数据，每次都打到 DB | 布隆过滤器 / 缓存空值 |
| 缓存击穿 | 热点 key 过期，大量请求同时打到 DB | 互斥锁 / 永不过期 + 异步更新 |
| 缓存雪崩 | 大量 key 同时过期 | 过期时间加随机值 / 多级缓存 |

### 6.2 AI 应用特有的缓存场景

```python
# 缓存 LLM 响应（相同 prompt 不重复调用，节省 token 费用）
import hashlib

def cache_key_for_llm(model: str, messages: list, temperature: float) -> str:
    # temperature > 0 时不应缓存（结果不确定）
    if temperature > 0:
        return None
    content = json.dumps({"model": model, "messages": messages}, sort_keys=True)
    return f"llm_cache:{hashlib.sha256(content.encode()).hexdigest()}"

# 缓存 embedding 结果（同一文本不重复调用 embedding API）
async def get_embedding(text: str, redis: Redis) -> list[float]:
    cache_key = f"emb:{hashlib.md5(text.encode()).hexdigest()}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    embedding = await openai_client.embeddings.create(input=text, model="text-embedding-3-small")
    result = embedding.data[0].embedding
    await redis.setex(cache_key, 86400, json.dumps(result))
    return result
```

---

## 七、数据库设计实战（AI 应用）

### 7.1 RAG 系统数据模型

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   documents  │────→│ document_chunks  │     │  conversations   │
│──────────────│     │──────────────────│     │──────────────────│
│ id           │     │ id               │     │ id               │
│ title        │     │ document_id (FK) │     │ user_id (FK)     │
│ file_path    │     │ content          │     │ title            │
│ file_type    │     │ embedding        │     │ created_at       │
│ status       │     │ chunk_index      │     └────────┬─────────┘
│ created_at   │     │ token_count      │              │
└──────────────┘     │ metadata (JSONB) │     ┌────────▼─────────┐
                     └──────────────────┘     │    messages      │
                                              │──────────────────│
                                              │ id               │
                                              │ conversation_id  │
                                              │ role             │
                                              │ content          │
                                              │ token_count      │
                                              │ model            │
                                              │ sources (JSONB)  │
                                              │ created_at       │
                                              └──────────────────┘
```

### 7.2 关键设计决策

**对话历史存储：**
- 短期（活跃对话）：Redis List/Stream，快速读写
- 长期（历史归档）：PostgreSQL，支持复杂查询和分析
- 超长对话：分页加载 + 摘要压缩（用 LLM 生成摘要替代早期消息）

**Embedding 存储策略：**
- 小规模（< 100 万向量）：pgvector 足够
- 中规模（100 万 - 1 亿）：Milvus / Qdrant
- 超大规模（> 1 亿）：Milvus 分布式集群 + 分片

---

## 八、面试高频题与回答模板

### Q1：你的项目中数据库是怎么设计的？

**回答框架：**
> 我们使用 PostgreSQL 作为主数据库，配合 pgvector 扩展做向量检索。核心表包括 users、documents、document_chunks、conversations、messages。文档上传后通过异步任务切片并生成 embedding 存入 document_chunks 表。用户提问时，先将问题转为向量，通过 pgvector 的 HNSW 索引检索 top-k 相关片段，拼接为 context 送入 LLM 生成回答。

### Q2：如何优化大量文档的向量检索性能？

**回答要点：**
1. 使用 HNSW 索引而非暴力搜索，将检索从 O(n) 降到 O(log n)
2. 合理设置 HNSW 参数：`m=16, ef_construction=200`（构建时），`ef_search=100`（查询时）
3. 预过滤：先用 WHERE 条件缩小范围（如 document_id），再做向量检索
4. 向量维度选择：如果精度够用，选 1024 维而非 1536 维
5. 数据量超过百万级考虑迁移到专用向量数据库（Milvus）

### Q3：如何保证数据库高可用？

**回答要点：**
1. 主从复制：PostgreSQL streaming replication，读写分离
2. 连接池：PgBouncer 减少连接开销
3. 监控告警：慢查询日志、连接数监控、磁盘空间
4. 备份策略：pg_dump 定期全量备份 + WAL 归档增量备份
5. 故障转移：Patroni 自动主从切换

### Q4：SQLAlchemy 异步和同步有什么区别？什么时候用异步？

**回答要点：**
> 异步 SQLAlchemy 基于 asyncpg（PostgreSQL）或 aiomysql（MySQL），配合 Python asyncio 事件循环，在等待数据库 IO 时不阻塞线程，适合高并发的 Web 应用（如 FastAPI）。同步模式适合脚本、数据迁移等场景。关键区别：异步需要用 `AsyncSession`、`async with`、`await`，且不能在异步上下文中使用懒加载（需要 `selectinload` / `joinedload` 预加载关联数据）。

### Q5：缓存和数据库的数据一致性怎么保证？

**回答要点：**
1. **Cache-Aside + 先更新 DB 再删缓存**（最常用，最终一致性）
2. 删除缓存而非更新缓存（避免并发写导致脏数据）
3. 设置合理的 TTL 作为兜底
4. 对强一致性要求高的场景（如扣费），直接读数据库不走缓存
5. 延迟双删：更新 DB → 删缓存 → 延迟 500ms 再删一次（防止并发读写导致脏缓存）

### Q6：项目中遇到过慢查询吗？怎么排查的？

**回答模板：**
> 遇到过。有一次对话历史查询变慢，排查步骤：
> 1. 开启慢查询日志定位到具体 SQL
> 2. EXPLAIN ANALYZE 发现全表扫描，缺少 `(user_id, created_at)` 联合索引
> 3. 添加索引后查询从 2s 降到 10ms
> 4. 同时发现 ORM 的 N+1 问题，改用 joinedload 预加载关联数据
> 5. 最终加了 Redis 缓存热点用户的最近对话列表

---

## 九、实战代码片段速查

### 9.1 完整的 FastAPI + SQLAlchemy + pgvector 检索

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

app = FastAPI()

@app.post("/search")
async def semantic_search(
    query: str,
    top_k: int = 5,
    db: AsyncSession = Depends(get_db),
):
    # 1. 生成查询向量
    query_embedding = await get_embedding(query)

    # 2. 向量检索
    stmt = (
        select(DocumentChunk)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )
    results = await db.execute(stmt)
    chunks = results.scalars().all()

    # 3. 构建 context
    context = "\n\n".join([c.content for c in chunks])

    # 4. 调用 LLM
    answer = await call_llm(query=query, context=context)

    return {
        "answer": answer,
        "sources": [{"id": c.id, "content": c.content[:200]} for c in chunks],
    }
```

### 9.2 数据库健康检查

```python
@app.get("/health/db")
async def db_health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```
