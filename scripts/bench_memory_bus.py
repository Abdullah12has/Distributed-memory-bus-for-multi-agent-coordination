#!/usr/bin/env python3
"""Microbenchmark for the memory-bus reference implementation (C4).

Measures the systems-performance numbers the thesis names as unmeasured
(Section "Limitations"): end-to-end write/read latency, the audit hash-chain
append + verify overhead, and policy-lattice check latency. Single-threaded,
identity compressor (no model on the critical path) so the numbers isolate the
bus machinery rather than the compressor.

REQUIRES Python 3.11+ (the m6 package uses datetime.UTC). Run inside the project
venv:

    .venv/bin/python3 scripts/bench_memory_bus.py --n 5000

Writes results/bus_bench/bench.json and prints a summary table. Hardware is
recorded in the JSON so the numbers are interpretable; report them as
"on <CPU>, single-threaded" in the manuscript.
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import tempfile
import time
from pathlib import Path

from m6.memory_bus.policy import Principal, enforce
from m6.memory_bus.schemas import (
    Classification,
    CompressedSlot,
    Fragment,
    TagVector,
    TextSummary,
)
from m6.memory_bus.service import MemoryBusService
from m6.memory_bus.storage.scratchpad import InMemoryScratchpad
from m6.memory_bus.storage.sqlite_audit import SQLiteAuditLog


class _IdentityCompressor:
    """CompressorAPI stub: copies the fragment text into a slot, no model.

    embed() returns None so the service skips the vector-store path entirely
    (service.write only calls vector_store.add when embed() is not None).
    """

    compressor_id = "identity"

    def compress(self, fragment: Fragment, target_ratio: float | None = None) -> CompressedSlot:
        return CompressedSlot(
            slot_id=f"slot-{fragment.fragment_id}-bench",
            payload=TextSummary(text=fragment.text),
            tags=fragment.tags,
            compressor_id="identity",
            ratio=1.0,
        )

    def embed(self, slot: CompressedSlot) -> list[float] | None:
        return None


class _NullVectorStore:
    """Never called (embed() returns None); present only to satisfy the ctor."""

    def add(self, *a, **k):  # pragma: no cover - defensive
        raise AssertionError("vector store should not be exercised in this bench")

    def search(self, *a, **k):  # pragma: no cover
        return []


def _pct(xs: list[float], p: float) -> float:
    return statistics.quantiles(xs, n=100)[int(p) - 1] if len(xs) > 1 else xs[0]


def _summary(latencies_ms: list[float]) -> dict:
    return {
        "n": len(latencies_ms),
        "median_ms": round(statistics.median(latencies_ms), 4),
        "mean_ms": round(statistics.fmean(latencies_ms), 4),
        "p95_ms": round(_pct(latencies_ms, 95), 4),
        "p99_ms": round(_pct(latencies_ms, 99), 4),
        "throughput_ops_s": round(1000.0 / statistics.fmean(latencies_ms), 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000, help="ops per measured phase")
    ap.add_argument("--warmup", type=int, default=500)
    ap.add_argument("--out", default="results/bus_bench/bench.json")
    args = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="bus_bench_"))
    audit = SQLiteAuditLog(tmp / "audit.db")
    bus = MemoryBusService(
        audit=audit,
        scratchpad=InMemoryScratchpad(ttl_seconds=3600, max_size=10**7),
        vector_store=_NullVectorStore(),
        compressor=_IdentityCompressor(),
    )
    # A realistic principal whose acl_mask fits signed-64 SQLite storage.
    # (Principal.super_user() uses acl_mask=2**64-1, which overflows the
    # audit-log INTEGER column — a separate bug tracked outside this bench.)
    principal = Principal(
        subject="bench-principal",
        acl_mask=(1 << 62),
        classification=Classification.SECRET,
    )
    tags = TagVector(acl_mask=0, classification=Classification.PUBLIC)

    def frag(i: int) -> Fragment:
        return Fragment(fragment_id=f"f{i}", text=f"benchmark fragment number {i} " * 8, tags=tags)

    # ---- policy.enforce() in isolation ---------------------------------- #
    for _ in range(args.warmup):
        enforce(principal, tags)
    pol = []
    for _ in range(args.n):
        t = time.perf_counter()
        enforce(principal, tags)
        pol.append((time.perf_counter() - t) * 1000)

    # ---- end-to-end write ---------------------------------------------- #
    for i in range(args.warmup):
        bus.write(principal, frag(i))
    writes = []
    slot_ids = []
    for i in range(args.warmup, args.warmup + args.n):
        t = time.perf_counter()
        resp = bus.write(principal, frag(i))
        writes.append((time.perf_counter() - t) * 1000)
        slot_ids.append(resp.slot_id)

    # ---- end-to-end read ----------------------------------------------- #
    reads = []
    for sid in slot_ids:
        t = time.perf_counter()
        bus.read(principal, sid)
        reads.append((time.perf_counter() - t) * 1000)

    # ---- audit hash-chain verify cost vs chain length ------------------ #
    t = time.perf_counter()
    ok = audit.verify()
    verify_ms = (time.perf_counter() - t) * 1000
    chain_len = args.warmup + args.n  # writes + reads each appended >=1 row

    out = {
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "python": platform.python_version(),
        },
        "config": {"n": args.n, "warmup": args.warmup},
        "policy_enforce": _summary(pol),
        "write_end_to_end": _summary(writes),
        "read_end_to_end": _summary(reads),
        "audit_verify": {
            "chain_rows_verified": chain_len,
            "verify_total_ms": round(verify_ms, 3),
            "verify_per_row_us": round(verify_ms * 1000 / max(chain_len, 1), 3),
            "chain_intact": bool(ok),
        },
    }
    audit.close()
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(out, indent=2))

    print(f"\nMemory-bus microbenchmark ({out['hardware']['processor']}, "
          f"single-threaded, identity compressor)\n")
    for k in ("policy_enforce", "write_end_to_end", "read_end_to_end"):
        s = out[k]
        print(f"  {k:18s} median={s['median_ms']:.4f} ms  p95={s['p95_ms']:.4f} ms  "
              f"~{s['throughput_ops_s']:,.0f} ops/s")
    v = out["audit_verify"]
    print(f"  audit_verify       {v['verify_per_row_us']:.2f} us/row over "
          f"{v['chain_rows_verified']:,} rows (intact={v['chain_intact']})")
    print(f"\nWrote {outp}")


if __name__ == "__main__":
    main()
