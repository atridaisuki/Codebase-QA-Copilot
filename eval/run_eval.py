"""
Phase 5 — Retrieval evaluation script.

Usage:
    python -m eval.run_eval              # run all configs
    python -m eval.run_eval --config hybrid+rerank
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so `app.*` imports work
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings  # noqa: E402
from app.schemas import SourceItem  # noqa: E402
from app.services.retrieval_service import RetrievalService  # noqa: E402

DATASET_PATH = Path(__file__).resolve().parent / "dataset.json"
RESULTS_DIR = Path(__file__).resolve().parent / "results"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class EvalCase:
    question: str
    expected_sources: list[str]
    expected_keywords: list[str]
    difficulty: str


@dataclass
class CaseResult:
    question: str
    difficulty: str
    expected_sources: list[str]
    returned_sources: list[str]
    hit_at: int | None  # 1-based rank of first hit, None if miss
    keyword_hits: list[str]
    keyword_misses: list[str]
    grounded: bool


@dataclass
class EvalMetrics:
    config_name: str
    total: int = 0
    recall_at_3: float = 0.0
    recall_at_5: float = 0.0
    mrr: float = 0.0
    precision_at_3: float = 0.0
    keyword_hit_rate: float = 0.0
    grounding_accuracy: float = 0.0
    elapsed_seconds: float = 0.0
    case_results: list[CaseResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Configs to compare
# ---------------------------------------------------------------------------
CONFIGS: list[dict] = [
    {"name": "vector_only", "enable_hybrid_search": False, "enable_rerank": False},
    {"name": "hybrid", "enable_hybrid_search": True, "enable_rerank": False},
    {"name": "hybrid+rerank", "enable_hybrid_search": True, "enable_rerank": True},
]


# ---------------------------------------------------------------------------
# Core evaluation logic
# ---------------------------------------------------------------------------
def load_dataset() -> list[EvalCase]:
    raw = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    return [EvalCase(**item) for item in raw]


def _source_matches(returned: str, expected: str) -> bool:
    """Check if a returned source path matches an expected source."""
    return Path(returned).name == Path(expected).name


def evaluate_retrieval(
    dataset: list[EvalCase],
    config: dict,
) -> EvalMetrics:
    """Run evaluation for a single config."""
    # --- apply config overrides via env vars ---
    import os

    os.environ["ENABLE_HYBRID_SEARCH"] = str(config.get("enable_hybrid_search", True))
    os.environ["ENABLE_RERANK"] = str(config.get("enable_rerank", True))

    # Clear cached settings so new env vars take effect
    get_settings.cache_clear()

    settings = get_settings()
    print(f"\n{'='*60}")
    print(f"Config: {config['name']}")
    print(f"  hybrid_search={settings.enable_hybrid_search}, rerank={settings.enable_rerank}")
    print(f"{'='*60}")

    service = RetrievalService()
    top_k = 5

    metrics = EvalMetrics(config_name=config["name"], total=len(dataset))
    recall_3_hits = 0
    recall_5_hits = 0
    mrr_sum = 0.0
    precision_3_sum = 0.0
    keyword_total = 0
    keyword_hit_total = 0
    grounding_correct = 0

    start = time.time()

    for case in dataset:
        _context, sources = service.retrieve(case.question, top_k=top_k)
        returned_sources = [s.source if isinstance(s, SourceItem) else s["source"] for s in sources]

        is_negative = len(case.expected_sources) == 0

        # --- Recall & MRR ---
        hit_at: int | None = None
        for rank, src in enumerate(returned_sources, start=1):
            if any(_source_matches(src, exp) for exp in case.expected_sources):
                hit_at = rank
                break

        if not is_negative:
            if hit_at is not None and hit_at <= 3:
                recall_3_hits += 1
            if hit_at is not None and hit_at <= 5:
                recall_5_hits += 1
            if hit_at is not None:
                mrr_sum += 1.0 / hit_at

            # Precision@3: how many of top-3 are relevant
            relevant_in_3 = sum(
                1
                for src in returned_sources[:3]
                if any(_source_matches(src, exp) for exp in case.expected_sources)
            )
            precision_3_sum += relevant_in_3 / min(3, max(len(returned_sources), 1))

        # --- Keyword hit rate ---
        if case.expected_keywords:
            keyword_total += len(case.expected_keywords)
            all_text = " ".join(returned_sources) + " " + _context
            hits = [kw for kw in case.expected_keywords if kw.lower() in all_text.lower()]
            misses = [kw for kw in case.expected_keywords if kw.lower() not in all_text.lower()]
            keyword_hit_total += len(hits)
        else:
            hits, misses = [], []

        # --- Grounding accuracy ---
        grounded = service.has_sufficient_evidence(case.question, sources)
        if is_negative:
            if not grounded:
                grounding_correct += 1
        else:
            if grounded:
                grounding_correct += 1

        case_result = CaseResult(
            question=case.question,
            difficulty=case.difficulty,
            expected_sources=case.expected_sources,
            returned_sources=returned_sources[:5],
            hit_at=hit_at,
            keyword_hits=hits,
            keyword_misses=misses,
            grounded=grounded,
        )
        metrics.case_results.append(case_result)

        status = "HIT" if hit_at else ("NEGATIVE" if is_negative else "MISS")
        print(f"  [{status}] {case.question[:50]}  (rank={hit_at}, grounded={grounded})")

    elapsed = time.time() - start
    positive_count = sum(1 for c in dataset if c.expected_sources)

    metrics.recall_at_3 = recall_3_hits / positive_count if positive_count else 0
    metrics.recall_at_5 = recall_5_hits / positive_count if positive_count else 0
    metrics.mrr = mrr_sum / positive_count if positive_count else 0
    metrics.precision_at_3 = precision_3_sum / positive_count if positive_count else 0
    metrics.keyword_hit_rate = keyword_hit_total / keyword_total if keyword_total else 0
    metrics.grounding_accuracy = grounding_correct / len(dataset) if dataset else 0
    metrics.elapsed_seconds = elapsed

    return metrics


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def print_summary(all_metrics: list[EvalMetrics]) -> None:
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    header = f"{'Config':<20} {'Recall@3':>9} {'Recall@5':>9} {'MRR':>7} {'P@3':>7} {'KW Hit':>7} {'Ground':>7} {'Time':>6}"
    print(header)
    print("-" * len(header))
    for m in all_metrics:
        print(
            f"{m.config_name:<20} {m.recall_at_3:>8.2f} {m.recall_at_5:>8.2f} "
            f"{m.mrr:>7.2f} {m.precision_at_3:>6.2f} {m.keyword_hit_rate:>6.2f} "
            f"{m.grounding_accuracy:>6.2f} {m.elapsed_seconds:>5.1f}s"
        )


def save_results(all_metrics: list[EvalMetrics]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = []
    for m in all_metrics:
        output.append({
            "config": m.config_name,
            "total": m.total,
            "recall_at_3": round(m.recall_at_3, 4),
            "recall_at_5": round(m.recall_at_5, 4),
            "mrr": round(m.mrr, 4),
            "precision_at_3": round(m.precision_at_3, 4),
            "keyword_hit_rate": round(m.keyword_hit_rate, 4),
            "grounding_accuracy": round(m.grounding_accuracy, 4),
            "elapsed_seconds": round(m.elapsed_seconds, 2),
            "cases": [
                {
                    "question": cr.question,
                    "difficulty": cr.difficulty,
                    "hit_at": cr.hit_at,
                    "grounded": cr.grounded,
                    "returned_sources": cr.returned_sources,
                    "keyword_hits": cr.keyword_hits,
                    "keyword_misses": cr.keyword_misses,
                }
                for cr in m.case_results
            ],
        })

    out_path = RESULTS_DIR / "eval_results.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nResults saved to {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    target_config = None
    if len(sys.argv) > 2 and sys.argv[1] == "--config":
        target_config = sys.argv[2]

    dataset = load_dataset()
    print(f"Loaded {len(dataset)} evaluation cases")

    configs = CONFIGS
    if target_config:
        configs = [c for c in CONFIGS if c["name"] == target_config]
        if not configs:
            print(f"Unknown config: {target_config}. Available: {[c['name'] for c in CONFIGS]}")
            sys.exit(1)

    all_metrics: list[EvalMetrics] = []
    for config in configs:
        metrics = evaluate_retrieval(dataset, config)
        all_metrics.append(metrics)

    print_summary(all_metrics)
    save_results(all_metrics)


if __name__ == "__main__":
    main()
