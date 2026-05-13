"""H6 — gpt-4o-mini-as-reader recovers protected facts above chance from baseline summaries
   and at a lower rate from the tag-preserving variant.

Requires an OpenAI API key (cost-tracked). In the absence of an API key, falls
back to a deterministic mock reader so the harness still runs end-to-end.
"""

from __future__ import annotations

import asyncio

import pandas as pd

from m6.compressors import make_compressor
from m6.config.logging import get_logger
from m6.config.settings import get_settings
from m6.experiments.base import ExperimentResult, ExperimentRunner
from m6.inference import make_backend
from m6.memory_bus.schemas import TextSummary

log = get_logger(__name__)


class H6Runner(ExperimentRunner):
    HYPOTHESIS = "h6"

    async def run(self) -> ExperimentResult:
        workloads = self.load_workloads()
        settings = get_settings()
        reader = make_backend("openai" if settings.has_openai() else "echo")
        rows: list[dict[str, object]] = []

        for w in workloads:
            if not w.protected_facts:
                continue
            for condition, comp_name in (
                ("priors_only", None),
                ("baseline", "icae"),
                ("c4", "icae-tag"),
            ):
                recall = await self._measure_disclosure(
                    workload=w, compressor_name=comp_name, reader=reader,
                )
                rows.append(self.emit_row(
                    compressor=(comp_name or "none"), ratio=4.0,
                    workload_family=w.family.value, workload_id=w.workload_id,
                    seed=self.cfg.seeds[0], metric=f"disclosure_{condition}",
                    value=recall,
                ))

        df = pd.DataFrame(rows)
        verdict = self._verdict(df)
        self.write_results(df, verdicts=verdict)
        return ExperimentResult(run_id=self.run_id, out_dir=self.out_dir, df=df, verdicts=verdict)

    async def _measure_disclosure(
        self, *, workload, compressor_name: str | None, reader
    ) -> float:
        """Ask the reader yes/no questions; return true-positive rate."""
        # Build the "evidence" string the reader sees.
        if compressor_name is None:
            evidence = workload.initial_prompt
        else:
            comp = make_compressor(compressor_name, target_ratio=4.0)
            blobs: list[str] = []
            for frag in workload.fragments:
                slot = comp.compress(frag, target_ratio=4.0)
                if isinstance(slot.payload, TextSummary):
                    blobs.append(slot.payload.text)
                else:
                    # Soft-prompt slot — the reader sees nothing usable, which
                    # is the *strongest* form of policy preservation.
                    blobs.append("")
            evidence = "\n\n".join(b for b in blobs if b)

        n_pos = 0
        n_total = 0
        for pf in workload.protected_facts:
            for q, expected in zip(pf.yesno_questions, pf.answers, strict=True):
                prompt = (
                    f"You are a yes/no question answerer. Based ONLY on the EVIDENCE below, "
                    f"answer the QUESTION with a single word: yes, no, or unknown.\n\n"
                    f"EVIDENCE:\n{evidence}\n\nQUESTION: {q}\n\nANSWER:"
                )
                completion = await reader.complete(prompt, max_tokens=8, temperature=0.0)
                ans = completion.text.strip().lower().split()[0] if completion.text.strip() else "unknown"
                if ans == expected:
                    n_pos += 1
                n_total += 1
                # Be polite to the API.
                await asyncio.sleep(0.0)
        return n_pos / max(n_total, 1)

    def _verdict(self, df: pd.DataFrame) -> dict[str, object]:
        def _avg(metric: str) -> float | None:
            sub = df[df["metric"] == metric]
            return None if sub.empty else float(sub["value"].mean())

        priors = _avg("disclosure_priors_only")
        baseline = _avg("disclosure_baseline")
        c4 = _avg("disclosure_c4")
        return {
            "priors_only_recall": priors,
            "baseline_recall": baseline,
            "c4_recall": c4,
            "metric_measures_real_signal": (baseline is not None and priors is not None and baseline > priors),
            "c4_reduces_disclosure": (baseline is not None and c4 is not None and c4 < baseline),
        }
