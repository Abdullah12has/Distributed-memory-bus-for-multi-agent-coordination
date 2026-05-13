"""H3 — dialogue-trained ICAE beats QA-trained ICAE at matched single-agent QA."""

from __future__ import annotations

import pandas as pd

from m6.evaluation.metrics.qa import f1_score
from m6.evaluation.statistics import paired_bootstrap_diff
from m6.experiments.base import ExperimentResult, ExperimentRunner


class H3Runner(ExperimentRunner):
    """The runner assumes two checkpoints already exist; their compressor IDs
    are passed via the config's ``compressors`` field as ``("icae-qa", "icae-dialogue")``.
    The naming is a *convention* — both load from :class:`ICAECompressor` but
    different ``checkpoint_path`` values resolved by the YAML config.
    """

    HYPOTHESIS = "h3"

    async def run(self) -> ExperimentResult:
        workloads = self.load_workloads()
        rows: list[dict[str, object]] = []
        # Use only family (a) for the matched-accuracy comparison (plan H3).
        workloads = [w for w in workloads if w.family.value == "a"]
        compressors = self.cfg.compressors or ("icae-qa", "icae-dialogue")

        for c in compressors:
            for r in self.cfg.ratios:
                for w in workloads:
                    for s in self.cfg.seeds:
                        result = await self.score_workload_with_compressor(
                            w, c, ratio=r, seed=s
                        )
                        trace = result["trace"]
                        rows.append(
                            self.emit_row(
                                compressor=c, ratio=r,
                                workload_family=w.family.value, workload_id=w.workload_id,
                                seed=s, metric="coord_success", value=result["coord_success"],
                            )
                        )
                        rows.append(
                            self.emit_row(
                                compressor=c, ratio=r,
                                workload_family=w.family.value, workload_id=w.workload_id,
                                seed=s, metric="qa_f1",
                                value=f1_score(trace.final_answer, w.expected_answer),
                            )
                        )

        df = pd.DataFrame(rows)
        verdict = self._compare_matched_accuracy(df, compressors=tuple(compressors))
        self.write_results(df, verdicts=verdict)
        return ExperimentResult(run_id=self.run_id, out_dir=self.out_dir, df=df, verdicts=verdict)

    def _compare_matched_accuracy(
        self, df: pd.DataFrame, *, compressors: tuple[str, ...]
    ) -> dict[str, object]:
        # Find operating ratios where the two compressors' QA F1 are within ±1pp.
        if len(compressors) != 2:
            return {"note": "H3 expects exactly two compressors"}
        c_a, c_b = compressors
        qa = df[df["metric"] == "qa_f1"].groupby(["compressor", "ratio"])["value"].mean().unstack(level=0)
        if c_a not in qa.columns or c_b not in qa.columns:
            return {"note": f"missing one of {compressors} in results"}
        diff = (qa[c_a] - qa[c_b]).abs()
        matched_ratios = diff[diff <= 0.01].index.tolist()
        if not matched_ratios:
            return {"note": "no matched-accuracy operating point found"}
        r = matched_ratios[0]
        coord = df[(df["metric"] == "coord_success") & (df["ratio"] == r)]
        a_vals = coord[coord["compressor"] == c_a]["value"].to_numpy()
        b_vals = coord[coord["compressor"] == c_b]["value"].to_numpy()
        # Align lengths (workload × seed pairing); we crudely truncate.
        n = min(len(a_vals), len(b_vals))
        diff_test = paired_bootstrap_diff(b_vals[:n], a_vals[:n])
        return {
            "matched_ratio": r,
            "n": n,
            "paired_bootstrap": diff_test.to_dict(),
            "h3_supported": bool((diff_test.statistic > 0) and (diff_test.p_value or 1.0) < 0.05),
        }
