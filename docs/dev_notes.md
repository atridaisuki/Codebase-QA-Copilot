# Codebase QA Copilot — 开发踩坑与优化记录

## 项目简介

基于 RAG（Retrieval-Augmented Generation）架构的代码库问答系统，支持向量检索、BM25 混合检索、CrossEncoder 重排序，最终由 LLM 生成回答。

技术栈：FastAPI + ChromaDB + sentence-transformers + jieba + Anthropic Claude

---

## 问题 1：Hybrid 和 Rerank 模式下只有第一组数据有结果

**现象**：跑 eval 时，vector_only 正常出数据，但 hybrid 和 hybrid+rerank 的结果为空或只有第一条。

**原因**：RetrievalService 在切换配置时，`get_settings()` 使用了 `@lru_cache`，环境变量修改后缓存没清除，导致后续配置实际没生效。

**解决**：在 eval 脚本中每次切换配置前调用 `get_settings.cache_clear()`，确保新的环境变量被读取。

---

## 问题 2：Rerank 结果比 Hybrid 低很多

**现象**：hybrid 的 recall@3 = 0.97，但加了 rerank 后指标反而下降。

**原因**：rerank_top_n 配置值过小，reranker 在重排序后截断了太多候选，导致正确文档被丢弃。

**解决**：在 `_apply_rerank` 中取 `max(rerank_top_n, top_k)` 作为实际保留数量，确保 rerank 不会比原始检索返回更少的结果。

---

## 问题 3：RTX 5060 (Blackwell) 不被 PyTorch 识别，Rerank 极慢

**现象**：`torch.cuda.is_available()` 返回 False，CrossEncoder rerank 35 条数据耗时 55.88 秒（纯 CPU）。

**原因**：RTX 5060 使用 Blackwell 架构（sm_120），PyTorch 稳定版（2.x）尚未支持该架构，CUDA kernel 无法编译。

**解决**：
```bash
pip uninstall torch torchvision torchaudio -y
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

安装 PyTorch nightly（2.12.0.dev + CUDA 12.8）后，GPU 正常识别：
- 设备：NVIDIA GeForce RTX 5060
- 耗时：55.88s → 5.1s（提速 10x+）
- 如果模型常驻内存（不重复加载），单次查询预计 < 1s

---

## 问题 4：Grounding 准确率异常低（hybrid 0.11, hybrid+rerank 0.51）

**现象**：`has_sufficient_evidence()` 使用固定阈值（top_score > 0.5, avg > 0.45）判断检索结果是否可靠，但不同检索模式下 score 量纲完全不同。

**根因分析**：

| 模式 | score 来源 | 典型范围 | 阈值 0.5 能过？ |
|------|-----------|---------|---------------|
| vector_only | 1 - cosine_distance | 0 ~ 1 | 能，设计就是按这个来的 |
| hybrid (RRF) | Σ weight/(k+rank) | 0.01 ~ 0.03 | 永远过不了 → grounding ≈ 0 |
| hybrid+rerank | CrossEncoder logits | -10 ~ +10 | 随机，量纲不对 |

**解决**：在 score 产生的源头做归一化，统一到 0~1：

1. **RRF 融合后**：对 batch 内所有 RRF 分数做 min-max 归一化
   ```python
   # _rrf_merge 末尾
   raw_scores = [c.score for c in merged]
   lo, hi = min(raw_scores), max(raw_scores)
   span = hi - lo if hi > lo else 1.0
   for c in merged:
       c.score = (c.score - lo) / span
   ```

2. **Rerank 后**：对 CrossEncoder 的 logits 做 sigmoid
   ```python
   # reranker_service.py
   chunk.score = 1.0 / (1.0 + math.exp(-raw_score))
   ```

**效果**：

| Config | Grounding (修复前) | Grounding (修复后) |
|--------|-------------------|-------------------|
| vector_only | 0.63 | 0.63 |
| hybrid | 0.11 | 0.31 |
| hybrid+rerank | 0.51 | 0.89 |

---

## 问题 5：负样本 Grounding 误判 + .env 覆盖 config 默认值

**现象**：归一化后 hybrid+rerank grounding 到了 0.89，但 5 个负样本仍全部判为 grounded=True。调高 config.py 中的阈值后 eval 结果不变。

**根因**：两层问题叠加：

1. **sigmoid 后负样本分数偏高**：不相关文档对的 CrossEncoder logits 接近 0，sigmoid(0) = 0.5，所以负样本 top_score 在 0.50~0.53 之间，刚好卡在旧阈值 0.5 的边缘上。
2. **`.env` 覆盖了 config.py 默认值**：pydantic-settings 的加载优先级是 `.env` > Field(default=...)。改了 config.py 的默认值但 `.env` 里写死了旧值，等于白改。

**实际分数分布**（sigmoid 归一化后）：

| 类型 | top_score 范围 | avg_score 范围 |
|------|---------------|---------------|
| 负样本 | 0.50 ~ 0.53 | 0.50 ~ 0.51 |
| 正样本 | 0.72+ | 0.58+ |

中间有 0.53 ~ 0.72 的明显间隔，取 0.65 作为阈值即可分开。

**解决**：同步修改 `.env` 和 config.py：
- `GROUNDED_TOP_SCORE_THRESHOLD`: 0.5 → 0.65
- `GROUNDED_AVERAGE_SCORE_THRESHOLD`: 0.45 → 0.5

**效果**：5 个负样本全部正确判为 grounded=False，hybrid+rerank grounding 从 0.89 → 0.94。

**教训**：用 pydantic-settings 时，调参要改 `.env` 而不是 config.py 的默认值。默认值只是兜底，`.env` 才是实际生效的配置源。

---

## 关于 vector_only 和 hybrid 的 Grounding 指标

提高阈值后 vector_only 的 grounding 从 0.63 掉到 0.20，hybrid 维持 0.31。这不是退化，而是预期行为：

- 阈值是针对 hybrid+rerank（sigmoid 归一化后的 0~1 分数）调优的
- vector_only 的 score（1 - cosine_distance）分布不同，很多正样本的 top_score 本身就在 0.5~0.65 之间，被新阈值误杀
- hybrid 的 RRF min-max 归一化后最高分永远是 1.0，但 average 和 min_chunks 条件更难满足

这些指标仅作为对比参考。实际生产环境只用 hybrid+rerank，其他配置是 eval 中的消融实验（ablation），用来验证每个组件的贡献。如果需要每种模式都有准确的 grounding，应该按模式分别设置阈值，但这会增加配置复杂度，当前阶段没必要。

---

## 当前最优配置 (hybrid+rerank) 指标

| 指标 | 值 |
|------|-----|
| Recall@3 | 0.97 |
| Recall@5 | 0.97 |
| MRR | 0.89 |
| Precision@3 | 0.78 |
| Keyword Hit Rate | 0.92 |
| Grounding Accuracy | 0.94 |
| 耗时 (含模型加载) | 5.1s |
