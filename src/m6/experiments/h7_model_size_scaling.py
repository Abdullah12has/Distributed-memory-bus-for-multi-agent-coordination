"""H7 — τ* shifts with model size across {7B, 13B, 34B-int4, 70B-int4}."""

from __future__ import annotations

import pandas as pd

from m6.evaluation.cliff_fitting import fit_piecewise
from m6.experiments.base import ExperimentResult, ExperimentRunner


class H7Runner(ExperimentRunner):
    """Runs the H2 procedure across model sizes.

    Compute-wise: 70B is **one ratio** (the suspected τ\* from 13B/34B), not
    a full sweep (plan §4.4). The model_size to use per run is controlled via
    ``configs/experiments/h7-{7b,13b,34b-int4,70b-int4}.yaml``.
    """

    HYPOTHESIS = "h7"

    async def run(self) -> ExperimentResult:
        workloads = self.load_workloads()
        rows: list[dict[str, object]] = []
        ratios = self.cfg.ratios
        compressors = self.cfg.compressors

        for c in compressors:
            for w in workloads:
                for r in ratios:
                    for s in self.cfg.seeds:
                        result = await self.score_workload_with_compressor(
                            w, c, ratio=r, seed=s
                        )
                        rows.append(self.emit_row(
                            compressor=c, ratio=r,
                            workload_family=w.family.value, workload_id=w.workload_id,
                            seed=s, metric="coord_success", value=result["coord_success"],
                            model_size=self.cfg.model_size,
                        ))

        df = pd.DataFrame(rows)
        verdict = self._fit_tau_per_size(df)
        self.write_results(df, verdicts=verdict)
        return ExperimentResult(run_id=self.run_id, out_dir=self.out_dir, df=df, verdicts=verdict)

    def _fit_tau_per_size(self, df: pd.DataFrame) -> dict[str, object]:
        per_family: dict[str, float] = {}
        for family, sub in df.groupby("workload_family"):
            agg = sub.groupby("ratio")["value"].mean().reset_index()
            if len(agg) < 4:
                continue
            fit = fit_piecewise(
                agg["ratio"].to_numpy(dtype=float),
                agg["value"].to_numpy(dtype=float),
            )
            per_family[str(family)] = fit.tau
        return {"tau_per_family": per_family, "model_size": self.cfg.model_size}
