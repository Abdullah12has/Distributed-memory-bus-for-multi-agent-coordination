"""H4 — tag preservation ≥85% at 4× with ≤5pp accuracy drop.

Accuracy delta is computed via a **paired bootstrap across all seeds**, not a
single-seed point estimate; the H4 falsification target (≤5 pp drop) needs a
CI to be meaningfully checkable.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from m6.compressors import make_compressor
from m6.compressors.tag_preserving import TagPreservingICAE
from m6.evaluation.metrics.tag_preservation import preservation_rate
from m6.evaluation.statistics import bootstrap_mean_ci, paired_bootstrap_diff
from m6.experiments.base import ExperimentResult, ExperimentRunner


class H4Runner(ExperimentRunner):
    HYPOTHESIS = "h4"

    async def run(self) -> ExperimentResult:
        workloads = self.load_workloads()
        rows: list[dict[str, object]] = []

        baseline = make_compressor("icae", target_ratio=4.0)
        c4 = make_compressor("icae-tag", target_ratio=4.0)
        assert isinstance(c4, TagPreservingICAE)
        _ = baseline  # keep the import; baseline coord runs go through score_workload_with_compressor.

        for r in (2.0, 4.0, 8.0):
            for w in workloads:
                # Tag preservation: deterministic given (fragment, compressor),
                # so it doesn't vary by seed. Emit one preservation row per
                # workload and copy it across seeds for downstream pivots.
                true_tags = [f.tags for f in w.fragments]
                slots = [c4.compress(f, target_ratio=r) for f in w.fragments]
                recovered = [c4.recover_tags(s) for s in slots]
                pres = preservation_rate(true_tags, recovered)
                for s in self.cfg.seeds:
                    rows.append(
                        self.emit_row(
                            compressor="icae-tag",
                            ratio=r,
                            workload_family=w.family.value,
                            workload_id=w.workload_id,
                            seed=s,
                            metric="preservation_rate",
                            value=pres.rate,
                        )
                    )
                    rows.append(
                        self.emit_row(
                            compressor="icae-tag",
                            ratio=r,
                            workload_family=w.family.value,
                            workload_id=w.workload_id,
                            seed=s,
                            metric="preservation_rate_acl",
                            value=pres.acl_rate,
                        )
                    )
                    rows.append(
                        self.emit_row(
                            compressor="icae-tag",
                            ratio=r,
                            workload_family=w.family.value,
                            workload_id=w.workload_id,
                            seed=s,
                            metric="preservation_rate_class",
                            value=pres.class_rate,
                        )
                    )

                # Accuracy delta vs baseline at the same ratio — paired across
                # seeds so each (workload, seed) pair contributes one matched
                # observation to the bootstrap.
                for s in self.cfg.seeds:
                    base_res = await self.score_workload_with_compressor(w, "icae", ratio=r, seed=s)
                    c4_res = await self.score_workload_with_compressor(
                        w, "icae-tag", ratio=r, seed=s
                    )
                    rows.append(
                        self.emit_row(
                            compressor="icae",
                            ratio=r,
                            workload_family=w.family.value,
                            workload_id=w.workload_id,
                            seed=s,
                            metric="coord_success_baseline",
                            value=base_res["coord_success"],
                        )
                    )
                    rows.append(
                        self.emit_row(
                            compressor="icae-tag",
                            ratio=r,
                            workload_family=w.family.value,
                            workload_id=w.workload_id,
                            seed=s,
                            metric="coord_success_c4",
                            value=c4_res["coord_success"],
                        )
                    )

        df = pd.DataFrame(rows)
        verdict = self._verdict(df)
        self.write_results(df, verdicts=verdict)
        return ExperimentResult(run_id=self.run_id, out_dir=self.out_dir, df=df, verdicts=verdict)

    def _verdict(self, df: pd.DataFrame) -> dict[str, object]:
        # Deduplicate preservation rows (same value across seeds) — one per workload.
        pres_4x_df = df[(df["ratio"] == 4.0) & (df["metric"] == "preservation_rate")]
        pres_4x_vals = pres_4x_df.drop_duplicates(subset=["workload_id"])["value"].to_numpy(
            dtype=np.float64
        )
        if pres_4x_vals.size > 0:
            pres_boot = bootstrap_mean_ci(pres_4x_vals)
            pres_4x = pres_boot.statistic
            pres_4x_ci_low = pres_boot.ci_low
        else:
            pres_4x = 0.0
            pres_4x_ci_low = 0.0

        base = df[(df["ratio"] == 4.0) & (df["metric"] == "coord_success_baseline")]
        c4 = df[(df["ratio"] == 4.0) & (df["metric"] == "coord_success_c4")]

        # Align (workload_id, seed) pairs explicitly so the bootstrap is paired.
        merged = base.merge(
            c4, on=["workload_id", "seed", "workload_family", "ratio"], suffixes=("_b", "_c4")
        )
        if merged.empty:
            return {
                "preservation_4x": pres_4x,
                "preservation_4x_ci_low": pres_4x_ci_low,
                "accuracy_delta_pp_4x": None,
                "h4_supported": False,
                "note": "no matched baseline/C4 rows at ratio=4.0",
            }

        a = merged["value_c4"].to_numpy(dtype=np.float64)
        b = merged["value_b"].to_numpy(dtype=np.float64)
        boot = paired_bootstrap_diff(a, b)
        delta_pp = boot.statistic * 100.0
        ci_low_pp = boot.ci_low * 100.0
        ci_high_pp = boot.ci_high * 100.0

        return {
            "preservation_4x": pres_4x,
            "preservation_4x_ci_low": pres_4x_ci_low,
            "accuracy_delta_pp_4x": delta_pp,
            "accuracy_delta_pp_4x_ci": [ci_low_pp, ci_high_pp],
            "paired_bootstrap": boot.to_dict(),
            # H4 supported ⟺ preservation CI lower bound ≥ 0.85
            # AND accuracy CI lower bound ≥ −5pp.
            "h4_supported": bool(pres_4x_ci_low >= 0.85 and ci_low_pp >= -5.0),
        }
