"""H1 — Spearman ρ(Δ_qa, Δ_coord) < 0.6 on ≥2 of 3 compressors at 7B."""

from __future__ import annotations

import numpy as np
import pandas as pd

from m6.evaluation.metrics.qa import f1_score
from m6.evaluation.statistics import spearman_rho
from m6.experiments.base import ExperimentResult, ExperimentRunner


class H1Runner(ExperimentRunner):
    HYPOTHESIS = "h1"

    async def run(self) -> ExperimentResult:
        workloads = self.load_workloads()
        rows: list[dict[str, object]] = []

        for c in self.cfg.compressors:
            for r in self.cfg.ratios:
                for w in workloads:
                    for s in self.cfg.seeds:
                        result = await self.score_workload_with_compressor(
                            w, c, ratio=r, seed=s
                        )
                        # Single-agent QA derivative: planner asks the initial
                        # prompt to a single agent. Approximated here by the
                        # deterministic family-solver's answer compared to
                        # ground truth.
                        trace = result["trace"]
                        qa_f1 = f1_score(trace.final_answer, w.expected_answer)
                        rows.append(
                            self.emit_row(
                                compressor=c, ratio=r,
                                workload_family=w.family.value, workload_id=w.workload_id,
                                seed=s, metric="qa_f1", value=qa_f1,
                            )
                        )
                        rows.append(
                            self.emit_row(
                                compressor=c, ratio=r,
                                workload_family=w.family.value, workload_id=w.workload_id,
                                seed=s, metric="coord_success", value=result["coord_success"],
                            )
                        )

        df = pd.DataFrame(rows)
        verdicts = self._compute_verdicts(df)
        self.write_results(df, verdicts=verdicts)
        return ExperimentResult(run_id=self.run_id, out_dir=self.out_dir, df=df, verdicts=verdicts)

    def _compute_verdicts(self, df: pd.DataFrame) -> dict[str, object]:
        # Pivot to wide: one row per (compressor, workload_id, seed, ratio)
        # with qa_f1 and coord_success columns.
        wide = df.pivot_table(
            index=["compressor", "workload_id", "seed", "ratio"],
            columns="metric", values="value", aggfunc="first",
        ).reset_index()
        out: dict[str, object] = {}
        n_below = 0
        for c, sub in wide.groupby("compressor"):
            ref = sub[sub["ratio"] == 1.0][["workload_id", "seed", "qa_f1", "coord_success"]]
            ref = ref.rename(columns={"qa_f1": "qa_f1_ref", "coord_success": "coord_ref"})
            merged = sub.merge(ref, on=["workload_id", "seed"], how="left")
            merged = merged[merged["ratio"] != 1.0].dropna(subset=["qa_f1", "coord_success", "qa_f1_ref", "coord_ref"])
            if merged.empty:
                out[c] = {"note": "no non-baseline rows"}
                continue
            delta_qa = merged["qa_f1"] - merged["qa_f1_ref"]
            delta_coord = merged["coord_success"] - merged["coord_ref"]
            rho_res = spearman_rho(delta_qa.to_numpy(), delta_coord.to_numpy())
            out[c] = rho_res.to_dict()
            if rho_res.statistic < 0.6:
                n_below += 1
        out["h1_supported"] = bool(n_below >= 2)
        return out
