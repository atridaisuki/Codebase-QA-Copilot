# 项目：Character Bot（角色扮演 Bot）

> 学习目标：Agent 编排层 —— 多步 LLM 调用如何协作
> 前置知识：RAG、Claude API、FastAPI、对话历史管理（均已掌握）

---

## 核心理念

一次用户消息，触发多次 LLM 调用，每次调用职责不同：

```
用户: "你今天怎么不说话"
        ↓
  ┌─ Step 1: 意图分析 ──────────────────────────┐
  │  输入: 用户消息 + 最近对话                      │
  │  输出: {intent: "关心", tone: "温和"}  (JSON)  │
  └──────────────────────────────────────────────┘
        ↓
  ┌─ Step 2: 状态更新 ──────────────────────────┐
  │  输入: 意图分析结果 + 当前情绪状态              │
  │  输出: {emotion: "touched", delta: +10}       │
  │  副作用: 更新情绪状态到存储                     │
  └──────────────────────────────────────────────┘
        ↓
  ┌─ Step 3: 内心独白 ──────────────────────────┐
  │  输入: 角色设定 + 情绪状态 + 意图分析 + 上下文   │
  │  输出: "他在关心我...虽然嘴上不想承认但有点开心"  │
  │  （用户看不到，但影响最终回复的语气和内容）       │
  └──────────────────────────────────────────────┘
        ↓
  ┌─ Step 4: 生成回复 ──────────────────────────┐
  │  输入: 角色设定 + 内心独白 + 情绪 + 对话历史     │
  │  输出: "...没有不说话，就是懒得理你而已。"       │
  └──────────────────────────────────────────────┘
        ↓
  ┌─ Step 5: 记忆提取（异步，不阻塞回复）──────────┐
  │  输入: 本轮完整对话                             │
  │  输出: {key_facts: ["他主动关心了我"], ...}     │
  │  副作用: 存入记忆库                             │
  └──────────────────────────────────────────────┘
```

这 5 步就是"编排"。每一步都是一次独立的 LLM 调用，有明确的输入输出，串起来就是一个 pipeline。

---

## 分版本实现（每个版本都是可运行的完整功能）

### v1 — 最小可用：角色设定 + 内心独白（2 次 LLM 调用）

**目标：** 学会"一个请求触发多次 LLM 调用"的基本模式

**功能：**
- 固定的角色设定（hardcode 一个 system prompt）
- 用户发消息 → 先生成内心独白 → 再基于独白生成回复
- 对话历史管理（复用你已有的经验）

**架构：**
```
app/
├── main.py                  # FastAPI 入口
├── config.py                # 配置（API key、角色设定路径等）
├── schemas.py               # 请求/响应模型
├── routers/
│   └── chat.py              # POST /chat 接口
├── services/
│   ├── llm_service.py       # Claude API 封装（复用经验）
│   └── character_service.py # 核心：编排内心独白 + 生成回复
├── core/
│   ├── prompts.py           # 各步骤的 prompt 模板
│   └── conversation.py      # 对话历史管理
└── characters/
    └── default.yaml         # 角色设定文件
```

**character_service.py 的核心逻辑（伪代码）：**
```python
class CharacterService:
    async def respond(self, user_message: str, history: list) -> CharacterResponse:
        # Step 1: 内心独白
        monologue = await self.llm.call(
            system="你是{角色名}。根据角色设定和对话，写出你的内心想法。",
            messages=history + [user_message],
        )

        # Step 2: 生成回复（把内心独白作为隐藏上下文）
        reply = await self.llm.call(
            system="你是{角色名}。根据你的内心想法，用符合角色的方式回复。",
            messages=history + [
                {"role": "assistant", "content": f"[内心独白]{monologue}"},
                {"role": "user", "content": user_message},
            ],
        )

        return CharacterResponse(reply=reply, monologue=monologue)
```

**你会学到：**
- async/await 在实际项目中的用法
- 多次 LLM 调用的串联：第一次的输出是第二次的输入
- prompt 模板设计：不同步骤的 prompt 怎么写

**角色设定文件示例 (characters/default.yaml)：**
```yaml
name: "冷月"
personality: |
  外冷内热的性格，嘴上总是很毒舌但其实很关心人。
  不会直接表达感情，习惯用反话。
  生气的时候会沉默，开心的时候会假装不在意。
speaking_style: |
  说话简短，不爱用语气词。
  偶尔会用"......"表示犹豫。
  从不用"哈哈"，觉得很傻。
background: |
  喜欢看书，尤其是推理小说。
  讨厌太吵的环境。
  有一只叫"团子"的猫。
```

**验收标准：** 发一条消息，能看到内心独白和最终回复两个部分，且回复风格符合角色设定。

---

### v2 — 情绪系统：让角色有"心情"（3 次 LLM 调用）

**目标：** 学会"状态管理" —— 跨对话保持和更新角色状态

**新增功能：**
- 角色有情绪状态（开心/平静/低落/生气/...），用数值表示
- 每次对话后更新情绪
- 情绪影响回复风格

**新增文件：**
```
app/
├── services/
│   └── emotion_service.py   # 情绪状态管理
└── models/
    └── character_state.py   # 角色状态数据模型
```

**情绪状态模型：**
```python
class EmotionState(BaseModel):
    primary: str = "neutral"       # 主要情绪: happy/calm/sad/angry/shy/...
    intensity: float = 0.5         # 强度 0~1
    description: str = "平静如水"   # 自然语言描述（塞进 prompt 用）
```

**编排变化：**
```python
async def respond(self, user_message: str, history: list) -> CharacterResponse:
    # 读取当前情绪
    emotion = self.emotion_service.get_state()

    # Step 1: 意图分析 + 情绪更新（新增）
    analysis = await self.llm.call(
        system="分析用户消息的意图，并判断角色的情绪会如何变化。输出 JSON。",
        messages=[...],
        # 用 structured output 让 Claude 输出固定格式
    )
    self.emotion_service.update(analysis)

    # Step 2: 内心独白（现在带上情绪）
    monologue = await self.llm.call(
        system=f"你是{角色名}。当前情绪：{emotion.description}。写出内心想法。",
        messages=[...],
    )

    # Step 3: 生成回复
    reply = await self.llm.call(
        system=f"你是{角色名}。当前情绪：{emotion.description}。根据内心想法回复。",
        messages=[...],
    )

    return CharacterResponse(reply=reply, monologue=monologue, emotion=emotion)
```

**你会学到：**
- Structured Output：让 Claude 输出 JSON 并用 Pydantic 解析
- 状态管理：情绪状态在对话之间持久化
- 状态如何影响行为：同一句话，不同情绪下回复完全不同

**验收标准：**
- 连续聊几句开心的话，角色情绪变好，回复语气变软
- 说一句伤人的话，情绪变差，回复变冷淡
- 能看到情绪状态的变化过程

---

### v3 — 记忆系统：让角色"记住"（RAG 复用）

**目标：** 把你已经会的 RAG 用在新场景 —— 存储和检索聊天记忆

**新增功能：**
- 每次对话后提取关键信息存入向量库
- 回复前检索相关记忆，让角色能提起之前聊过的事

**新增文件：**
```
app/
├── services/
│   ├── memory_service.py     # 记忆存储和检索
│   └── memory_extractor.py   # 从对话中提取关键信息
```

**记忆提取（对话结束后异步执行，不阻塞回复）：**
```python
class MemoryExtractor:
    async def extract(self, conversation: list[Message]) -> list[Memory]:
        # 调用 LLM 从对话中提取关键事实
        result = await self.llm.call(
            system="从这段对话中提取值得记住的关键信息。输出 JSON 列表。",
            messages=conversation,
        )
        # 返回结构化记忆
        # [
        #   {"fact": "用户说他下周要考试", "importance": 0.8, "topic": "学业"},
        #   {"fact": "用户喜欢吃火锅", "importance": 0.5, "topic": "饮食偏好"},
        # ]
```

**编排变化（在 Step 2 内心独白之前加一步记忆检索）：**
```python
# Step 0: 检索相关记忆（你已经会的 RAG）
memories = self.memory_service.search(user_message, top_k=3)
# → ["用户上周说下周要考试", "用户喜欢吃火锅"]

# 把记忆塞进后续步骤的 prompt 里
memory_context = "\n".join(f"- {m}" for m in memories)
```

**你会学到：**
- RAG 的新用法：不是检索文档，而是检索对话记忆
- 异步任务：记忆提取不阻塞回复（asyncio.create_task）
- 信息提取：让 LLM 从非结构化对话中提取结构化数据

**验收标准：**
- 告诉角色"我明天要考试"
- 隔几轮对话后，角色主动提起"你考试怎么样了？"

---

### v4 — 好感度系统 + 多用户支持

**目标：** 学会"多实例状态管理" —— 同一个角色对不同用户有不同状态

**新增功能：**
- 每个用户有独立的好感度（0~100）
- 好感度影响角色的态度和亲密程度
- 好感度随时间自然衰减

**新增文件：**
```
app/
├── services/
│   └── affinity_service.py   # 好感度管理
└── storage/
    └── sqlite_store.py       # SQLite 持久化（替代内存存储）
```

**你会学到：**
- SQLite 做轻量持久化（比内存 dict 可靠，比 PostgreSQL 简单）
- 多用户状态隔离：每个 user_id 有独立的情绪、记忆、好感度
- 定时任务：好感度衰减（可以用 FastAPI 的 lifespan 或 APScheduler）

---

## 技术栈

```
后端:       FastAPI（你已经会了）
LLM:        Claude API（你已经会了）
向量库:     Chroma（你已经会了，v3 记忆系统用）
持久化:     SQLite（v4 新学，很简单）
配置:       YAML 角色设定 + pydantic-settings
测试前端:   简单的 HTML 页面 或 命令行交互（不花时间在前端）
```

不引入任何新框架（不用 LlamaIndex、不用 LangChain）。
所有编排逻辑手写，这样你能完全理解每一步在干什么。

## 对接 QQ Bot（可选，做完 v2 之后随时可以接）

你之前用过 NoneBot，对接很简单：
- 你的 FastAPI 提供 `POST /chat` 接口
- NoneBot 插件里收到消息 → 调你的接口 → 返回回复
- 或者直接在 NoneBot 插件里 import 你的 character_service

不建议一开始就接 QQ Bot，先用 HTTP 接口或命令行测试，
确认编排逻辑没问题了再接，避免同时调试两个东西。

---

## 每个版本的学习重点总结

```
v1 (内心独白):
  核心学习: 多次 LLM 调用串联，一次的输出是下一次的输入
  新概念:   prompt 模板分离，async/await
  代码量:   约 200 行核心代码
  预计时间: 这个你自己把握，不给时间预估

v2 (情绪系统):
  核心学习: 状态管理，structured output
  新概念:   让 LLM 输出 JSON，Pydantic 解析验证
  代码量:   在 v1 基础上 +150 行

v3 (记忆系统):
  核心学习: RAG 的新应用场景，异步任务
  新概念:   asyncio.create_task，信息提取
  代码量:   在 v2 基础上 +200 行（大部分可以从 QA Copilot 搬过来）

v4 (好感度 + 多用户):
  核心学习: 多实例状态管理，持久化
  新概念:   SQLite，定时任务
  代码量:   在 v3 基础上 +150 行
```

## 和上一个项目的关系

```
从 Codebase QA Copilot 直接复用:
  ├── Claude API 调用封装 (llm_service.py 的经验)
  ├── 对话历史管理 (conversation_store.py 的经验)
  ├── 向量检索 (v3 记忆系统，embedding + chroma)
  └── FastAPI 项目结构

新学的东西:
  ├── 多步 LLM 编排（v1 核心）
  ├── Structured Output / JSON 模式（v2）
  ├── 异步任务 asyncio.create_task（v3）
  ├── SQLite 持久化（v4）
  └── YAML 配置加载（v1）
```
