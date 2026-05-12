# ADR-005: Cryptographic commitment infrastructure — deferred to D7

**Status:** Accepted (decision = defer)
**Date:** 2026-05-12
**Deciders:** Syed Abdullah Hassan, Lauri Lovén

## Context

The FCG architecture documents (`integrator-architecture.pdf` and `software-architecture.pdf`) describe a cryptographic commitment infrastructure — transcript hash chains across markets (`H_j = Hash(bids_j, alloc_j, payments_j, {H_k : k ∈ adj(j)})`), Bayesian type tracking (`L_t = ρ·L_{t-1} + log(Pr(z_t | strategic) / Pr(z_t | honest))`), audit deposit sizing (`B ≥ Δ̄/Pr(detected | δ)`). These are part of the doctoral-phase trilogy (Lovén, *Real-Time AI Service Economy* + *Trustworthy Marketplace Architecture* + *Collusion, Learning, and Dynamic Credibility*, plan §9.5).

The thesis (plan §1) explicitly defers production-grade governance enforcement to the doctoral phase. The tag-preserving compressor (C4) is *the research instrument* for measuring whether per-slot tags survive compression — **not** a cryptographic commitment.

## Decision

* The thesis ships a **hash chain over audit-log rows** that is structurally analogous to the FCG mechanism but does not pretend to be the full cryptographic commitment story. See [`TECHNICAL_REFERENCE.md` §3.3](../TECHNICAL_REFERENCE.md#33-the-audit-log).
* The full cryptographic commitment infrastructure — deposit sizing, slashing penalties, recursive credibility of the audit infrastructure — is deferred to D7.
* The thesis manuscript names this gap explicitly in Chapter 10 (Discussion).

## Options considered

### Option A — Implement the full commitment infrastructure now

Pros: complete picture. Cons: drastically out of scope; would push the thesis past 10 months. The cryptographic side is one of D7's stated deliverables (plan §6.3, §8).

### Option B — Implement a hash chain only *(chosen)*

Pros: gives D7 a working seam. Provides tamper-evidence at the audit-log level. Cheap to test. Cons: not a real cryptographic commitment; an attacker with write access to the SQLite file can re-hash the chain. (This is documented explicitly in the model card.)

### Option C — Implement nothing

Pros: most honest. Cons: gives D7 no seam at all; the hash-chain machinery is the seam.

## Trade-off analysis

Option B is the minimum that makes the FCG-integration claim ("the FCG team can adopt the API without rewriting the compression layer", plan §2.4) operational. The full cryptographic commitment is D7's territory.

## Consequences

**Easier.**
* D7 can swap SQLite for Postgres with cryptographic-grade timestamps without changing the API surface.
* Tamper-detection tests work today (the chain breaks on edit).

**Harder.**
* Reviewers may push back on the "audit log" framing; the model card addresses this directly: this is a research-grade audit log, not a compliance-grade one.

**Revisit when.**
* D7 implements a real commitment scheme. The audit-log table schema is the migration target.

## Action items

1. [x] Implement the chain hash trigger in `m6.memory_bus.storage.sqlite_audit`.
2. [x] Write the model card stating what this hash chain is and is not.
3. [ ] Mention the gap in thesis Chapter 7 explicitly and link it to D7.
