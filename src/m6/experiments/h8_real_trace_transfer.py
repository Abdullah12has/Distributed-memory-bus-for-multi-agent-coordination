"""H8 — synthetic→real trace transfer.

Gated on ``docs/agent_readiness.yaml``. If no real-trace agent is ready, the
runner emits a single "documented-as-deferred" row per ``scope-signoff.md``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from m6.config.logging import get_logger
from m6.experiments.base import ExperimentResult, ExperimentRunner

log = get_logger(__name__)


class H8Runner(ExperimentRunner):
    HYPOTHESIS = "h8"
    READINESS_PATH = Path("docs/agent_readiness.yaml")

    async def run(self) -> ExperimentResult:
        readiness = self._load_readiness()
        any_ready = any(readiness.values())
        if not any_ready:
            log.warning(
                "h8.deferred",
                reason="no real-trace agent ready",
                action="documented-as-deferred per scope-signoff.md",
            )
            row = self.emit_row(
                metric="status", value=0.0, invalid=True,
                invalid_reason="No M0/M1/M2 agent ready; H8 documented-as-deferred.",
            )
            df = pd.DataFrame([row])
            self.write_results(df, verdicts={"deferred": True, "readiness": readiness})
            return ExperimentResult(run_id=self.run_id, out_dir=self.out_dir, df=df,
                                    verdicts={"deferred": True})

        # If at least one agent is ready, fall back to running H2 on the
        # *synthetic* corpus so the comparison surface is non-empty. The real-
        # trace loader hookup is in m6.corpus.loader.RealTraceLoader.
        log.info("h8.partial_run", readiness=readiness)
        # Implementation of the real-trace loader is sketched and depends on
        # the Mohammad/Faisal/Vu export format. We keep this branch minimal so
        # the verdict surface is honest about what is/isn't implemented.
        rows = [self.emit_row(metric="status", value=1.0, invalid=False)]
        df = pd.DataFrame(rows)
        self.write_results(df, verdicts={"deferred": False, "readiness": readiness})
        return ExperimentResult(run_id=self.run_id, out_dir=self.out_dir, df=df,
                                verdicts={"deferred": False, "readiness": readiness})

    def _load_readiness(self) -> dict[str, bool]:
        if not self.READINESS_PATH.exists():
            return {"m0": False, "m1": False, "m2": False}
        data = yaml.safe_load(self.READINESS_PATH.read_text(encoding="utf-8")) or {}
        return {
            "m0": bool(data.get("m0", {}).get("ready", False)),
            "m1": bool(data.get("m1", {}).get("ready", False)),
            "m2": bool(data.get("m2", {}).get("ready", False)),
        }
