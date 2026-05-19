# Scope sign-off

> **Status template.** This document is the artefact the plan (§4.1 Month 0) calls for: a written confirmation of scope with Lauri before any code is written. The body below is the *template* to be filled in during the 60-minute sign-off meeting.

## Meeting

* **Date:** _to be filled in_
* **Attendees:** Syed Abdullah Hassan (author), Lauri Lovén (academic supervisor).
* **Optional:** Asim Nadeem / Oskari Valkama (TalentAdore, by email).

## Decisions to confirm in writing

### Decision 1 — FCG-integration deliverable

> The FCG-integration deliverable is a **reference implementation** — a FastAPI service exposing the memory-bus API with documented contracts and a single-machine deployment — **not** a live production integration on the FCG agentic platform.

* [ ] Confirmed by Lauri.
* Notes:

### Decision 2 — Synthetic benchmark carries the thesis

> The synthetic Vignette-7 benchmark (C1) carries the thesis evaluation.

* [ ] Confirmed by Lauri.
* Notes:

### Decision 3 — Compute envelope

> All training and evaluation runs on a **single M4 Pro 48 GB** workstation with MLX, llama.cpp, and Ollama. There are no contingent paths on external clusters. The primary evaluation is at 7B with a 13B sanity arm.

* [ ] Confirmed by Lauri.
* Notes:

### Decision 4 — Out of scope

The following are **not** in scope for this thesis:

* Production-grade governance enforcement. C4 is a research prototype with measured properties.
* Cross-tokenizer / cross-model-family compressed exchange.
* Live production deployment on the FCG platform.

* [ ] Confirmed by Lauri.
* Notes:

### Decision 5 — Stretch goals (Month 8)

At most **TWO** of S1–S4 (plan §4.5) will be selected at end of Month 7 based on Lauri's input.

* [ ] Confirmed by Lauri.
* Notes:

### Decision 6 — Mid-thesis review (Month 5)

A **formal ~90-minute review** with Lauri will occur at the end of Month 5. If two or more chapters are not in reviewable state by then, stretch goals (Month 8) are dropped and the time is reallocated to writing.

* [ ] Confirmed by Lauri.
* Notes:

## Sign-off

* Author signature & date:
* Supervisor signature & date:
