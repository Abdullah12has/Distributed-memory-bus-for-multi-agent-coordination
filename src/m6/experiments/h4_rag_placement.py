"""H4 — RAG pipeline placement P1 vs P2 vs P3, storage-bounded vs accuracy-bounded."""

from __future__ import annotations

import pandas as pd

from m6.benchmark.schemas import WorkloadFamily
from m6.compressors import make_compressor
from m6.evaluation.metrics.qa import f1_score
from m6.experiments.base import ExperimentResult, ExperimentRunner
from m6.pipelines import Pipeline1, Pipeline2, Pipeline3


class H4Runner(ExperimentRunner):
    HYPOTHESIS = "h4"

    async def run(self) -> ExperimentResult:
        workloads = [w for w in self.load_workloads() if w.family is WorkloadFamily.CROSS_DOC_FACT_AGGREGATION]
        rows: list[dict[str, object]] = []

        for c in self.cfg.compressors:
            comp = make_compressor(c, target_ratio=self.cfg.ratios[0] or 4.0)
            for budget_mode in ("storage_bounded", "accuracy_bounded"):
                pipelines = {
                    "P1": Pipeline1(comp, target_ratio=self.cfg.ratios[0] or 4.0),
                    "P2": Pipeline2(comp, target_ratio=self.cfg.ratios[0] or 4.0),
                    "P3": Pipeline3(comp, target_ratio=self.cfg.ratios[0] or 4.0),
                }
                for w in workloads:
                    corpus = list(w.fragments)
                    for p_name, pipe in pipelines.items():
                        pipe.build(corpus)
                        hits = pipe.query(w.initial_prompt, k=5)
                        synthesized = " ; ".join(h.fragment.text[:200] for h in hits)
                        f1 = f1_score(synthesized, w.expected_answer)
                        for s in self.cfg.seeds:
                            rows.append(
                                self.emit_row(
                                    compressor=c, pipeline=p_name,
                                    workload_family=w.family.value, workload_id=w.workload_id,
                                    seed=s, metric="f1", value=f1,
                                    actual_ratio=self.cfg.ratios[0] or 4.0,
                                )
                            )

        df = pd.DataFrame(rows)
        self.write_results(df, verdicts={"note": "H4 verdict computation deferred to analysis notebook."})
        return ExperimentResult(run_id=self.run_id, out_dir=self.out_dir, df=df)
