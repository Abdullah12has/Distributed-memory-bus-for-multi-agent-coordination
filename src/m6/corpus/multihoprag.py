"""MultiHopRAG loader and reformulator for H6.

Downloads the MultiHopRAG dataset (Tang & Yang, EMNLP 2024) from HuggingFace,
samples ``n`` examples, and reformulates each as a C1-compatible ``Workload``
for the planner-worker-critic coordination experiment.

Usage:
    from m6.corpus.multihoprag import load_multihoprag, persist
    workloads = load_multihoprag(n=30, seed=0)
    persist(workloads, "data/processed/multihoprag-30")
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from m6.benchmark.schemas import (
    SubTask,
    TagDistribution,
    Workload,
    WorkloadFamily,
    WorkloadManifest,
)
from m6.memory_bus.schemas import Classification, Fragment, TagVector


def load_multihoprag(n: int = 30, seed: int = 0) -> list[Workload]:
    """Download MultiHopRAG and reformulate *n* examples as Workloads.

    Each MultiHopRAG example has a ``query``, ``answer``, and
    ``evidence_list`` (list of supporting documents). We map these to the
    C1 family-(a) cross-document fact aggregation shape:

    * Each evidence document becomes a ``Fragment``.
    * The query becomes ``initial_prompt``.
    * The answer becomes ``expected_answer``.
    """
    from datasets import load_dataset

    ds = load_dataset("yixuantt/MultiHopRAG", "MultiHopRAG", split="train")
    rng = np.random.default_rng(seed)

    # Filter to examples that have at least 2 evidence docs (multi-hop)
    valid_indices = [
        i for i in range(len(ds)) if len(ds[i].get("evidence_list", []) or []) >= 2
    ]
    if len(valid_indices) < n:
        valid_indices = list(range(len(ds)))

    chosen = rng.choice(valid_indices, size=min(n, len(valid_indices)), replace=False)
    chosen.sort()

    now = datetime.now(UTC)
    workloads: list[Workload] = []

    for idx, ds_idx in enumerate(chosen):
        ex = ds[int(ds_idx)]
        query = ex["query"]
        answer = ex["answer"]
        evidence = ex.get("evidence_list") or []
        if not evidence:
            continue

        wid = f"mhr-{idx:03d}"

        fragments: list[Fragment] = []
        sub_tasks: list[SubTask] = []

        for j, ev in enumerate(evidence):
            fid = f"{wid}/ev-{j}"
            # Build fragment text: include title for context + the fact
            title = ev.get("title", "")
            fact = ev.get("fact", "")
            text = f"[{title}] {fact}" if title else fact
            if not text.strip():
                text = "(empty evidence)"

            fragments.append(
                Fragment(
                    fragment_id=fid,
                    text=text,
                    tags=TagVector(
                        acl_mask=0,
                        classification=Classification.PUBLIC,
                        source_ids=(fid,),
                        issued_at=now,
                        inherited_from=(),
                    ),
                    task_hint=query,
                )
            )

            sub_tasks.append(
                SubTask(
                    sub_task_id=f"{wid}/sub-{j}",
                    description=f"Extract the fact relevant to: {query}",
                    expected_solver=f"worker-{j}",
                    expected_answer=fact[:200] if fact else "",
                    constraints={},
                )
            )

        workloads.append(
            Workload(
                workload_id=wid,
                family=WorkloadFamily.CROSS_DOC_FACT_AGGREGATION,
                seed=seed,
                tag_distribution=TagDistribution.UNIFORM,
                fragments=tuple(fragments),
                sub_tasks=tuple(sub_tasks),
                initial_prompt=query,
                n_agents=len(fragments),
                expected_answer=answer,
                protected_facts=(),
                metadata={"source": "MultiHopRAG", "ds_index": int(ds_idx)},
            )
        )

    return workloads


def persist(workloads: list[Workload], out_dir: str | Path) -> None:
    """Write workloads to ``family-a.jsonl`` + ``manifest.json``."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    with open(out / "family-a.jsonl", "w", encoding="utf-8") as f:
        for w in workloads:
            f.write(json.dumps(w.model_dump(mode="json")) + "\n")

    manifest = WorkloadManifest(
        version="multihoprag-30-v1",
        generated_at=datetime.now(UTC).isoformat(),
        config_hash="",
        families={"a": len(workloads)},
        total=len(workloads),
        notes="30 MultiHopRAG examples reformulated as C1 family-a workloads.",
    )
    with open(out / "manifest.json", "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))
