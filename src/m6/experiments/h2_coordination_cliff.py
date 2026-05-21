"""H2 — coordination cliff τ* exists, varies by workload, not by compressor."""

from __future__ import annotations

import numpy as np
import pandas as pd

from m6.evaluation.cliff_fitting import fit_piecewise
from m6.evaluation.statistics import holm_correction, mann_whitney_u
from m6.experiments.base import ExperimentResult, ExperimentRunner


class H2Runner(ExperimentRunner):
    HYPOTHESIS = "h2"

    async def run(self) -> ExperimentResult:
        workloads = self.load_workloads()
        rows: list[dict[str, object]] = []
        # Denser ratio sweep around suspected cliff (plan H2).
        ratios = self.cfg.ratios or (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0)

        for c in self.cfg.compressors:
            for w in workloads:
                for r in ratios:
                    for s in self.cfg.seeds:
                        result = await self.score_workload_with_compressor(w, c, ratio=r, seed=s)
                        rows.append(
                            self.emit_row(
                                compressor=c,
                                ratio=r,
                                workload_family=w.family.value,
                                workload_id=w.workload_id,
                                seed=s,
                                metric="coord_success",
                                value=result["coord_success"],
                            )
                        )

        df = pd.DataFrame(rows)
        verdicts = self._compute_verdicts(df)
        self.write_results(df, verdicts=verdicts)
        return ExperimentResult(run_id=self.run_id, out_dir=self.out_dir, df=df, verdicts=verdicts)

    def _compute_verdicts(self, df: pd.DataFrame) -> dict[str, object]:
        per_cell: list[dict[str, object]] = []
        # Track which per_cell indices have a Mann-Whitney test so Holm
        # correction aligns correctly even when some cells are skipped.
        tested_indices: list[int] = []
        p_values: list[float] = []
        for (c, family), sub in df.groupby(["compressor", "workload_family"]):
            agg = sub.groupby("ratio")["value"].mean().reset_index()
            ratios = agg["ratio"].to_numpy(dtype=float)
            success = agg["value"].to_numpy(dtype=float)
            if len(ratios) < 4 or float(np.ptp(success)) < 1e-6:
                continue
            fit = fit_piecewise(ratios, success, bounds=(float(ratios.min()), float(ratios.max())))
            # Mann-Whitney U: success below vs above tau are independent samples
            # (drawn across different (workload, seed, ratio) cells). The
            # alternative "greater" tests that the below-τ distribution is
            # stochastically larger than the above-τ distribution.
            below = sub[sub["ratio"] < fit.tau]["value"].to_numpy()
            above = sub[sub["ratio"] >= fit.tau]["value"].to_numpy()
            if below.size > 0 and above.size > 0:
                test = mann_whitney_u(below, above, alternative="greater")
                tested_indices.append(len(per_cell))
                p_values.append(test.p_value or 1.0)
            else:
                test = None
            per_cell.append(
                {
                    "compressor": c,
                    "workload_family": family,
                    "tau": fit.tau,
                    "slope_left": fit.slope_left,
                    "slope_right": fit.slope_right,
                    "drop_rel": fit.drop_rel,
                    "rmse": fit.rmse,
                    "test_method": "mann_whitney_u",
                    "test_p": (test.p_value if test else None),
                    "test_p_holm": None,
                    "n_below": int(below.size),
                    "n_above": int(above.size),
                }
            )

        # Apply Holm correction only to tested cells, aligning by tracked index.
        adjusted = holm_correction(p_values) if p_values else []
        for cell_idx, adj in zip(tested_indices, adjusted, strict=False):
            per_cell[cell_idx]["test_p_holm"] = adj

        # "varies by workload but not by compressor within ±20%" check.
        df_fits = pd.DataFrame(per_cell)
        tau_spread_ok: dict[str, bool] = {}
        if not df_fits.empty:
            for family, fam_sub in df_fits.groupby("workload_family"):
                taus = fam_sub["tau"].to_numpy(dtype=float)
                spread = (taus.max() - taus.min()) / max(taus.mean(), 1e-6)
                tau_spread_ok[str(family)] = bool(spread <= 0.20)

        # Gate the verdict on both the 30% drop AND statistical significance.
        if not df_fits.empty:
            sig_mask = pd.to_numeric(df_fits["test_p_holm"], errors="coerce").fillna(1.0) < 0.05
            drop_mask = df_fits["drop_rel"].ge(0.30)
            supported = bool((sig_mask & drop_mask).mean() >= 0.5)
        else:
            supported = False

        return {
            "per_cell": per_cell,
            "tau_spread_within_20pct_per_family": tau_spread_ok,
            "h2_supported": supported,
        }
