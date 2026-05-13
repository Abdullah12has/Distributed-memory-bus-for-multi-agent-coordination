"""Institutional corpus loader + real-trace loader (H8).

Reference: ``docs/TECHNICAL_REFERENCE.md`` §6.3.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from m6.config.logging import get_logger
from m6.corpus.pii_redaction import redact

log = get_logger(__name__)


@dataclass(frozen=True)
class CorpusDocument:
    """One document from the institutional subset."""

    doc_id: str
    source: str                         # "m0" | "m1" | "m2" | "bookcorpus"
    text: str
    redaction_counts: dict[str, int]


class InstitutionalCorpus:
    """Loads the curated institutional subset; refuses to yield un-redacted text."""

    def __init__(self, root: Path | str, *, use_ner: bool = False) -> None:
        self.root = Path(root)
        self.use_ner = use_ner

    def iter_documents(self) -> Iterator[CorpusDocument]:
        for src_dir in sorted(self.root.glob("*")):
            if not src_dir.is_dir():
                continue
            source = src_dir.name.lower()
            for f in sorted(src_dir.glob("*.txt")):
                text = f.read_text(encoding="utf-8")
                redacted, report = redact(text, use_ner=self.use_ner)
                yield CorpusDocument(
                    doc_id=f"{source}/{f.stem}",
                    source=source,
                    text=redacted,
                    redaction_counts={
                        "emails": report.emails, "phones": report.phones,
                        "ibans": report.ibans, "ips": report.ips,
                        "persons": report.persons, "organizations": report.organizations,
                    },
                )


class RealTraceLoader:
    """Loads real M0/M1/M2 traces for H8.

    The exact wire format is decided by Mohammad / Faisal / Vu; we keep the
    interface narrow so a per-source adapter can be written without touching
    the runner.
    """

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    def workloads(self) -> Iterator[object]:
        """Yield :class:`m6.benchmark.schemas.Workload` instances. Stubbed for now.

        The real implementation parses the trace exports into the same
        :class:`Workload` shape as the synthetic generator so the H2/H7
        pipelines work unmodified.
        """
        if not self.root.exists():
            log.warning("corpus.real_trace_root_missing", path=str(self.root))
            return
        log.warning(
            "corpus.real_trace_loader_stub",
            note="Per-source adapter to be written when M0/M1/M2 export format is fixed.",
        )
        yield from ()
