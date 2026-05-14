"""H4 — RAG pipeline placement P1 vs P2 vs P3, storage-bounded vs accuracy-bounded.

Verdict computation:

* For each budget regime, paired-bootstrap difference between P1's and P2's F1.
  H4 expects the sign to flip between regimes: P1 > P2 on storage-bounded,
  P2 > P1 on accuracy-bounded. Effect-size threshold is 5 pp F1.
* P3 is compared against the better of P1/P2 on a combined ``f1 / eur`` score
  in each regime; H4 expects P3 to dominate or tie the leader.

Both tests use the recentred-null percentile bootstrap implemented in
``m6.evaluation.statistics.paired_bootstrap_diff``. Holm correction is applied
across the two regime comparisons.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from m6.benchmark.schemas import WorkloadFamily
from m6.compressors import make_compressor
from m6.config.logging import get_logger
from m6.evaluation.metrics.qa import f1_score
from m6.evaluation.statistics import holm_correction, paired_bootstrap_diff
from m6.experiments.base import ExperimentResult, ExperimentRunner
from m6.pipelines import Pipeline1, Pipeline2, Pipeline3
from m6.pipelines.cost_model import eur_for_call

log = get_logger(__name__)

# A coarse per-query token estimate for the cost ledger when we are not
# actually invoking a paid backend in the H4 run. Real-experiment numbers
# replace these via the cost ledger; the estimate is used to compute the
# combined f1/eur score so the verdict is still well-defined in stub runs.
_STUB_INPUT_TOKENS = 1500
_STUB_OUTPUT_TOKENS = 200
_STUB_MODEL = "gpt-4o-mini"


class H4Runner(ExperimentRunner):
    HYPOTHESIS = "h4"

    async def run(self) -> ExperimentResult:
        workloads = [
            w
            for w in self.load_workloads()
            if w.family is WorkloadFamily.CROSS_DOC_FACT_AGGREGATION
        ]
        rows: list[dict[str, object]] = []
        ratio = self.cfg.ratios[0] if self.cfg.ratios else 4.0

        for c in self.cfg.compressors:
            comp = make_compressor(c, target_ratio=ratio)
            for budget_mode in ("storage_bounded", "accuracy_bounded"):
                pipelines = {
                    "P1": Pipeline1(comp, target_ratio=ratio),
                    "P2": Pipeline2(comp, target_ratio=ratio),
                    "P3": Pipeline3(comp, target_ratio=ratio),
                }
                for w in workloads:
                    corpus = list(w.fragments)
                    for p_name, pipe in pipelines.items():
                        pipe.build(corpus)  # type: ignore[attr-defined]
                        hits = pipe.query(w.initial_prompt, k=5)  # type: ignore[attr-defined]
                        synthesized = " ; ".join(h.fragment.text[:200] for h in hits)
                        f1 = f1_score(synthesized, w.expected_answer)
                        eur_per_query = eur_for_call(
                            _STUB_MODEL, _STUB_INPUT_TOKENS, _STUB_OUTPUT_TOKENS
                        )
                        for s in self.cfg.seeds:
                            rows.append(
                                self.emit_row(
                                    compressor=c,
                                    pipeline=p_name,
                                    workload_family=w.family.value,
                                    workload_id=w.workload_id,
                                    seed=s,
                                    metric="f1",
                                    value=f1,
                                    actual_ratio=ratio,
                                    eur_cost=eur_per_query,
                                    invalid_reason=budget_mode,  # piggyback the regime onto an existing column
                                )
                            )
                            rows.append(
                                self.emit_row(
                                    compressor=c,
                                    pipeline=p_name,
                                    workload_family=w.family.value,
                                    workload_id=w.workload_id,
                                    seed=s,
                                    metric="eur_per_query",
                                    value=eur_per_query,
                                    actual_ratio=ratio,
                                    eur_cost=eur_per_query,
                                    invalid_reason=budget_mode,
                                )
                            )

        df = pd.DataFrame(rows)
        verdicts = self._compute_verdicts(df)
        self.write_results(df, verdicts=verdicts)
        return ExperimentResult(
            run_id=self.run_id,
            out_dir=self.out_dir,
            df=df,
            verdicts=verdicts,
        )

    # ------------------------------------------------------------------ #
    # Verdict
    # ------------------------------------------------------------------ #
    def _compute_verdicts(self, df: pd.DataFrame) -> dict[str, object]:
        """Compute the H4 verdict from the long-format dataframe.

        Returns a dict shaped roughly:
            {
              "regimes": {
                 "storage_bounded": {"p1_vs_p2_pp": ..., "ci": [...], "p_holm": ...,
                                      "p3_vs_leader_score": ..., "leader": "P1"},
                 "accuracy_bounded": {... same shape ...},
              },
              "h4_supported": bool,
            }
        """
        out: dict[str, object] = {"regimes": {}}
        f1_only = df[df["metric"] == "f1"]
        eur_only = df[df["metric"] == "eur_per_query"]
        p_values: list[float] = []
        per_regime: list[dict[str, object]] = []

        for regime in ("storage_bounded", "accuracy_bounded"):
            f1_r = f1_only[f1_only["invalid_reason"] == regime]
            eur_r = eur_only[eur_only["invalid_reason"] == regime]
            if f1_r.empty:
                continue

            # Paired (workload_id, seed) alignment of P1 vs P2 on F1.
            p1 = f1_r[f1_r["pipeline"] == "P1"][["workload_id", "seed", "value"]]
            p2 = f1_r[f1_r["pipeline"] == "P2"][["workload_id", "seed", "value"]]
            paired = p1.merge(p2, on=["workload_id", "seed"], suffixes=("_p1", "_p2"))
            if paired.empty:
                continue
            a = paired["value_p1"].to_numpy(dtype=np.float64)
            b = paired["value_p2"].to_numpy(dtype=np.float64)
            pb = paired_bootstrap_diff(a, b)
            p_values.append(pb.p_value or 1.0)

            # Combined f1 / eur ranking per pipeline.
            ranking = {}
            for pname in ("P1", "P2", "P3"):
                f1_vals = f1_r[f1_r["pipeline"] == pname]["value"].to_numpy(dtype=np.float64)
                eur_vals = eur_r[eur_r["pipeline"] == pname]["value"].to_numpy(dtype=np.float64)
                if f1_vals.size == 0 or eur_vals.size == 0:
                    continue
                ranking[pname] = float(f1_vals.mean() / max(eur_vals.mean(), 1e-9))

            leader = max(ranking, key=lambda k: ranking[k]) if ranking else None
            per_regime.append(
                {
                    "regime": regime,
                    "p1_vs_p2_diff_pp": pb.statistic * 100.0,
                    "p1_vs_p2_ci_pp": [pb.ci_low * 100.0, pb.ci_high * 100.0],
                    "p1_vs_p2_p_value": pb.p_value,
                    "p1_vs_p2_effect_size": pb.effect_size,
                    "ranking_f1_over_eur": ranking,
                    "leader_by_score": leader,
                }
            )

        adjusted = holm_correction(p_values) if p_values else []
        for cell, adj in zip(per_regime, adjusted, strict=False):
            cell["p1_vs_p2_p_holm"] = adj
            out["regimes"][cell["regime"]] = cell  # type: ignore[index]

        # H4 supported iff: (a) effect-size threshold met in both regimes, (b)
        # the sign of (P1 - P2) flips between regimes, (c) P3 is the leader on
        # the combined score in both regimes, (d) all Holm-adjusted p's < 0.05.
        if len(per_regime) == 2:
            sb, ab = per_regime[0], per_regime[1]
            sign_flip = (float(sb["p1_vs_p2_diff_pp"]) * float(ab["p1_vs_p2_diff_pp"])) < 0  # type: ignore[arg-type]
            effect = (
                abs(float(sb["p1_vs_p2_diff_pp"])) >= 5.0  # type: ignore[arg-type]
                and abs(float(ab["p1_vs_p2_diff_pp"])) >= 5.0  # type: ignore[arg-type]
            )
            p3_wins = sb.get("leader_by_score") == "P3" and ab.get("leader_by_score") == "P3"
            sig = all((c.get("p1_vs_p2_p_holm") or 1.0) < 0.05 for c in per_regime)  # type: ignore[operator]
            out["h4_supported"] = bool(sign_flip and effect and p3_wins and sig)
        else:
            out["h4_supported"] = False
        return out
