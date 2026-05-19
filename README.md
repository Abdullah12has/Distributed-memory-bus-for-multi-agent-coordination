# m6-thesis — Distributed Memory Bus for Multi-Agent Campus Systems

> *Context Compression, Coordination Quality, and Policy-Aware Sharing.*
> Master's thesis (M6) at the University of Oulu · Faculty of ITEE · CSE Research Unit, **Future Computing Group**.
> Author: **Syed Abdullah Hassan**.  Supervisor: **Lauri Lovén**.  Industry: **TalentAdore** (Asim Nadeem, Oskari Valkama).

This repository is the reference implementation and evaluation harness that accompanies the thesis manuscript described in [`plan.md`](plan.md). It is the deliverable. It is not, and is not intended as, a production deployment on the FCG platform.

The single-machine compute envelope is fixed: one **Apple M4 Pro, 48 GB**. Every wallclock estimate in [`docs/TECHNICAL_REFERENCE.md`](docs/TECHNICAL_REFERENCE.md) is dimensioned for that machine.

## Quick start

```bash
# 1. Clone + create the project venv (Python 3.11).
make venv install-dev

# 2. Copy the env file. No API keys are required for the default run; every
#    headline experiment uses local backends (MLX/Ollama for 7B/13B).
#    Optional paid arms exist under
#    configs/experiments/*-openai.yaml.
cp .env.example .env

# 3. Run the memory bus reference service.
make bus-dev
# → http://localhost:8080/docs

# 4. Generate the C1 benchmark v0.1 (3 workload families, 150 instances).
make bench-generate

# 5. Reproduce the headline figure for Chapter 5 (coordination cliff).
make reproduce-ch5
```

## What lives where

| Path | Purpose |
|------|---------|
| [`plan.md`](plan.md) | The thesis implementation plan (canonical scope). |
| [`docs/TECHNICAL_REFERENCE.md`](docs/TECHNICAL_REFERENCE.md) | The technical document that grounds the codebase. **Read this before writing any code.** |
| [`docs/HYPOTHESIS_IMPLEMENTATION_PLAN.md`](docs/HYPOTHESIS_IMPLEMENTATION_PLAN.md) | H1–H4: what the code has to compute, in what order, with what statistical protocol. |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System architecture, three-layer memory bus. |
| [`docs/adr/`](docs/adr/) | Architecture Decision Records for the major choices (compressor family, storage stack, agent runtime, inference backends). |
| `src/m6/` | Importable library. See module map below. |
| `configs/` | YAML configs per experiment, training run, model, and benchmark generation. |
| `scripts/` | Reproduction shell scripts and model-download helpers. |
| `tests/` | `pytest` unit + integration tests. |
| `docker/` | CPU + CUDA Dockerfiles and `docker-compose.yml`. |
| `thesis_latex/` | The LaTeX manuscript (pre-existing). |

## Module map (`src/m6/`)

```
m6/
├── benchmark/         # C1 — workload generator, tags, coordination metrics
├── compressors/       # C2 + C4 — LLMLingua-2, ICAE, instruction-aware filter, tag-preserving variant
├── pipelines/         # C3 — P1 compress→retrieve, P2 retrieve→compress, P3 joint
├── memory_bus/        # FastAPI reference service: write / read / subscribe / audit
├── agents/            # AutoGen planner-worker-critic loop and scratchpad bridge
├── inference/         # MLX / llama.cpp / Ollama / OpenAI / Anthropic backends
├── evaluation/        # QA, coordination, hallucination, tag-preservation, disclosure metrics + statistics
├── experiments/       # One runner per hypothesis (H1–H4)
├── corpus/            # Institutional-subset loader + PII redaction
├── config/            # Pydantic settings, structured logging, OTel hooks
├── utils/             # Seed control, IO helpers, trace formatting
└── cli.py             # Typer-based CLI entry-point — `m6 <command>`
```

## Reproducibility

Every headline figure has a single command:

```bash
make reproduce-ch5   # Coordination cliff (H1, H2)
make reproduce-ch6   # RAG pipelines (H3) + cost analysis
make reproduce-ch7   # Tag preservation (H4)
```

Five seeds per condition, bootstrap CI, paired bootstrap for compressor-vs-compressor comparisons, Mann-Whitney U for the cliff-detection test, Holm correction within hypothesis families. See [`docs/TECHNICAL_REFERENCE.md` §10](docs/TECHNICAL_REFERENCE.md) for the full protocol.

## Citation

If you use this repository, please cite the thesis. Until the manuscript is on file, cite as:

```bibtex
@misc{hassan2026memorybus,
  author = {Hassan, Syed Abdullah},
  title  = {Distributed Memory Bus for Multi-Agent Campus Systems},
  year   = {2026},
  school = {University of Oulu, Faculty of ITEE, CSE Research Unit},
  note   = {Master's thesis, supervised by Lauri Lov\'en}
}
```

## License

Proprietary — University of Oulu / TalentAdore. Discuss with the author and supervisor before redistribution.
