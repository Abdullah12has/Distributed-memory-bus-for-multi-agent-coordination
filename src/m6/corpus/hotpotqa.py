"""HotpotQA loader and reformulator for cliff sweep validation.

Downloads HotpotQA (Yang et al., EMNLP 2018) from HuggingFace,
samples ``n`` multi-hop examples, and reformulates each as a C1-compatible
``Workload`` for the coordination cliff sweep experiment.

Usage:
    from m6.corpus.hotpotqa import load_hotpotqa, persist
    workloads = load_hotpotqa(n=50, seed=0)
    persist(workloads, "data/processed/hotpotqa-50")
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


def load_hotpotqa(n: int = 50, seed: int = 0) -> list[Workload]:
    """Download HotpotQA and reformulate *n* examples as Workloads.

    Each HotpotQA example has a ``question``, ``answer``, and ``context``
    (list of titled paragraphs with sentences). We map these to the C1
    family-(a) cross-document fact aggregation shape:

    * Each context paragraph becomes a ``Fragment``.
    * The question becomes ``initial_prompt``.
    * The answer becomes ``expected_answer``.
    """
    from datasets import load_dataset

    ds = load_dataset("hotpotqa/hotpot_qa", "distractor", split="validation")
    rng = np.random.default_rng(seed)

    # Filter to 'bridge' or 'comparison' types with >= 2 supporting facts
    valid_indices = []
    for i in range(len(ds)):
        ex = ds[i]
        sf_titles = ex.get("supporting_facts", {}).get("title", [])
        n_unique = len(set(sf_titles))
        if n_unique >= 2 and len(ex.get("context", {}).get("title", [])) >= 2:
            valid_indices.append(i)

    if len(valid_indices) < n:
        valid_indices = list(range(len(ds)))

    chosen = rng.choice(valid_indices, size=min(n, len(valid_indices)), replace=False)
    chosen.sort()

    now = datetime.now(UTC)
    workloads: list[Workload] = []

    for idx, ds_idx in enumerate(chosen):
        ex = ds[int(ds_idx)]
        question = ex["question"]
        answer = ex["answer"]
        ctx = ex.get("context", {})
        titles = ctx.get("title", [])
        sentences_list = ctx.get("sentences", [])

        if not titles:
            continue

        wid = f"hqa-{idx:03d}"
        fragments: list[Fragment] = []
        sub_tasks: list[SubTask] = []

        for j, (title, sents) in enumerate(zip(titles, sentences_list)):
            fid = f"{wid}/ctx-{j}"
            text = f"[{title}] " + " ".join(sents)
            if not text.strip():
                text = "(empty context)"

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
                    task_hint=question,
                )
            )

            sub_tasks.append(
                SubTask(
                    sub_task_id=f"{wid}/sub-{j}",
                    description=f"Extract facts relevant to: {question}",
                    expected_solver=f"worker-{j}",
                    expected_answer=" ".join(sents)[:200],
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
                initial_prompt=question,
                n_agents=len(fragments),
                expected_answer=answer,
                protected_facts=(),
                metadata={"source": "HotpotQA", "ds_index": int(ds_idx)},
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
        version="hotpotqa-50-v1",
        generated_at=datetime.now(UTC).isoformat(),
        config_hash="",
        families={"a": len(workloads)},
        total=len(workloads),
        notes=f"{len(workloads)} HotpotQA examples reformulated as C1 family-a workloads.",
    )
    with open(out / "manifest.json", "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))
