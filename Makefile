# =============================================================================
# Makefile — m6-thesis
#
# Conventions:
#   * Every target is `.PHONY` (we do not produce target-named files).
#   * `make help` lists every target with its docstring (single # immediately
#     after target name is the docstring).
#   * All Python invocations use the project venv at `.venv/`. The venv path is
#     overrideable via `VENV=...` for CI that wants a different location.
#   * Long-running training/inference targets are tagged with a trailing comment
#     marker like `# WALLCLOCK 5-10d` so a glance at the file tells you which
#     targets are cheap and which are not.
# =============================================================================

SHELL          := /bin/bash
PYTHON         ?= python3.11
VENV           ?= .venv
PIP            := $(VENV)/bin/pip
PY             := $(VENV)/bin/python
PYTEST         := $(VENV)/bin/pytest
RUFF           := $(VENV)/bin/ruff
MYPY           := $(VENV)/bin/mypy
UVICORN        := $(VENV)/bin/uvicorn
COMPOSE        := docker compose
COMPOSE_FILE   := docker/docker-compose.yml
IMAGE_TAG      ?= m6-thesis:dev

# Detect platform so we can install the right extras automatically.
UNAME_S        := $(shell uname -s)
UNAME_M        := $(shell uname -m)
ifeq ($(UNAME_S),Darwin)
ifeq ($(UNAME_M),arm64)
    EXTRAS := torch,mlx,inference,agents,rag,external,eval,dev
else
    EXTRAS := torch,inference,agents,rag,external,eval,dev
endif
else
    EXTRAS := torch,inference,agents,rag,external,eval,dev
endif

.DEFAULT_GOAL := help
.PHONY: help

help: ## Show this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "  \033[1;36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------
.PHONY: venv install install-dev install-all sync-requirements upgrade-pip

venv: ## Create the project virtualenv at .venv/.
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel

install: venv ## Install the base runtime only (no training stack).
	$(PIP) install -e .

install-dev: venv ## Install runtime + dev tooling (default for contributors).
	$(PIP) install -e ".[$(EXTRAS)]"
	$(VENV)/bin/pre-commit install
	@echo "✓ dev environment ready at $(VENV)/"

install-all: install-dev ## Alias kept for muscle memory.

upgrade-pip: ## Upgrade pip/setuptools/wheel in the venv.
	$(PIP) install --upgrade pip setuptools wheel

sync-requirements: ## Regenerate requirements.txt from pyproject.toml (advisory).
	@echo "→ Lockfile regeneration is intentionally manual; see docs/dev/lockfile.md"

# -----------------------------------------------------------------------------
# Quality gates
# -----------------------------------------------------------------------------
.PHONY: lint fmt typecheck test test-fast test-integration check pre-commit

lint: ## Ruff lint (no fixes).
	$(RUFF) check src tests

fmt: ## Ruff format + import sort, in place.
	$(RUFF) format src tests
	$(RUFF) check --fix --select I src tests

typecheck: ## mypy strict over src/.
	$(MYPY) src/m6

test-fast: ## Run unit tests only, parallel, no coverage.
	$(PYTEST) -n auto --no-cov tests/unit

test: ## Run unit + integration tests with coverage.
	$(PYTEST) tests

test-integration: ## Run integration tests (slower).
	$(PYTEST) -m integration tests

check: lint typecheck test ## Run every quality gate (CI entry-point).

pre-commit: ## Run all pre-commit hooks on the working tree.
	$(VENV)/bin/pre-commit run --all-files

# -----------------------------------------------------------------------------
# Memory bus service
# -----------------------------------------------------------------------------
.PHONY: bus-dev bus-prod bus-openapi

bus-dev: ## Run the memory bus FastAPI service with hot-reload (port 8080).
	$(UVICORN) m6.memory_bus.api:app --reload --host 0.0.0.0 --port 8080

bus-prod: ## Run the memory bus service with production settings.
	$(UVICORN) m6.memory_bus.api:app --host 0.0.0.0 --port 8080 --workers 1 --log-config configs/uvicorn-prod.json

bus-openapi: ## Dump the OpenAPI schema to docs/openapi.json.
	$(PY) -m m6.memory_bus.openapi_dump > docs/openapi.json
	@echo "✓ wrote docs/openapi.json"

# -----------------------------------------------------------------------------
# Benchmark (C1)
# -----------------------------------------------------------------------------
.PHONY: bench-generate bench-validate bench-release

bench-generate: ## Regenerate the C1 benchmark v0.1 (150 instances, 3 families).
	$(PY) -m m6.benchmark.cli generate --config configs/benchmark/c1-v0.1.yaml --out data/processed/c1-v0.1

bench-validate: ## Sanity-check the generated benchmark (schema + invariants).
	$(PY) -m m6.benchmark.cli validate --path data/processed/c1-v0.1

bench-release: bench-generate bench-validate ## Produce a release-ready C1 tarball.
	tar -czvf dist/c1-v0.1.tar.gz -C data/processed c1-v0.1
	@echo "✓ wrote dist/c1-v0.1.tar.gz"

# -----------------------------------------------------------------------------
# Training (compressors)
# -----------------------------------------------------------------------------
.PHONY: train-icae train-icae-tags train-dialogue

train-icae: ## Train ICAE-style soft-prompt compressor (7B LoRA, dual-objective). # WALLCLOCK ~3d
	$(PY) -m m6.compressors.training.train_icae --config configs/training/icae-7b.yaml

train-icae-tags: ## Train tag-preserving ICAE variant (C4).                       # WALLCLOCK ~3d
	$(PY) -m m6.compressors.training.train_icae --config configs/training/icae-7b-tags.yaml

train-dialogue: ## H3 ablation: train on planner-worker-critic dialogue traces.   # WALLCLOCK ~3d
	$(PY) -m m6.compressors.training.train_icae --config configs/training/icae-7b-dialogue.yaml

# -----------------------------------------------------------------------------
# Experiments per hypothesis
# -----------------------------------------------------------------------------
.PHONY: exp-h1 exp-h2 exp-h3 exp-h4 exp-h5 exp-h6 exp-h7 exp-h8 exp-all

exp-h1: ## H1 — QA accuracy vs coordination success correlation (7B).             # WALLCLOCK ~2d
	$(PY) -m m6.experiments.cli run --hypothesis h1 --config configs/experiments/h1.yaml

exp-h2: ## H2 — coordination cliff τ* (7B + 13B sub-sample).                       # WALLCLOCK ~5-10d
	$(PY) -m m6.experiments.cli run --hypothesis h2 --config configs/experiments/h2.yaml

exp-h3: ## H3 — training distribution: QA vs dialogue (matched compute).          # WALLCLOCK ~2d
	$(PY) -m m6.experiments.cli run --hypothesis h3 --config configs/experiments/h3.yaml

exp-h4: ## H4 — RAG pipeline placement (P1/P2/P3, storage vs accuracy bounded).   # WALLCLOCK ~3d
	$(PY) -m m6.experiments.cli run --hypothesis h4 --config configs/experiments/h4.yaml

exp-h5: ## H5 — tag preservation ≥85% at 4× with ≤5pp accuracy drop.              # WALLCLOCK ~1d
	$(PY) -m m6.experiments.cli run --hypothesis h5 --config configs/experiments/h5.yaml

exp-h6: ## H6 — summary-level inference disclosure (held-out reader = gpt-4o-mini).# WALLCLOCK ~1d
	$(PY) -m m6.experiments.cli run --hypothesis h6 --config configs/experiments/h6.yaml

exp-h7: ## H7 — model-size scaling of τ* (13B fp16 + 34B int4 + 70B int4).        # WALLCLOCK ~3w
	$(PY) -m m6.experiments.cli run --hypothesis h7 --config configs/experiments/h7.yaml

exp-h8: ## H8 — real M0/M1/M2 trace transfer (gated on connector readiness).      # WALLCLOCK depends
	$(PY) -m m6.experiments.cli run --hypothesis h8 --config configs/experiments/h8.yaml

exp-all: exp-h1 exp-h2 exp-h3 exp-h4 exp-h5 exp-h6 exp-h7 exp-h8 ## Run every hypothesis (long).

# -----------------------------------------------------------------------------
# Reproduction (chapter headline figures)
# -----------------------------------------------------------------------------
.PHONY: reproduce-ch5 reproduce-ch6 reproduce-ch7 reproduce-ch8 reproduce-all

reproduce-ch5: ## Headline figure for Chapter 5 (coordination cliff).
	./scripts/reproduce_chapter5.sh

reproduce-ch6: ## Headline figure for Chapter 6 (RAG pipelines).
	./scripts/reproduce_chapter6.sh

reproduce-ch7: ## Headline figure for Chapter 7 (tag preservation + disclosure).
	./scripts/reproduce_chapter7.sh

reproduce-ch8: ## Headline figure for Chapter 8 (model-size scaling).
	./scripts/reproduce_chapter8.sh

reproduce-all: reproduce-ch5 reproduce-ch6 reproduce-ch7 reproduce-ch8 ## Reproduce all chapter figures.

# -----------------------------------------------------------------------------
# Docker
# -----------------------------------------------------------------------------
.PHONY: docker-build docker-build-cuda docker-up docker-down docker-logs docker-shell

docker-build: ## Build the CPU/MPS docker image (Apple-Silicon-aware base).
	$(COMPOSE) -f $(COMPOSE_FILE) build memory-bus

docker-build-cuda: ## Build the CUDA variant for Linux+NVIDIA hosts.
	docker build -f docker/Dockerfile.cuda -t $(IMAGE_TAG)-cuda .

docker-up: ## Bring up the memory bus + dependencies (detached).
	$(COMPOSE) -f $(COMPOSE_FILE) up -d

docker-down: ## Tear down docker-compose stack.
	$(COMPOSE) -f $(COMPOSE_FILE) down --remove-orphans

docker-logs: ## Tail container logs.
	$(COMPOSE) -f $(COMPOSE_FILE) logs -f --tail=200

docker-shell: ## Drop into a shell in the memory-bus container.
	$(COMPOSE) -f $(COMPOSE_FILE) exec memory-bus /bin/bash

# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
.PHONY: models-pull models-pull-7b models-pull-13b models-pull-34b models-pull-70b

models-pull: models-pull-7b ## Default pull = 7B for fast iteration.

models-pull-7b: ## Pull Llama-3.1-8B-Instruct in MLX + Ollama formats.
	./scripts/download_models.sh llama-3.1-8b-instruct

models-pull-13b: ## Pull a 13B-class model (Llama-3.1 / Qwen2.5 14B).
	./scripts/download_models.sh qwen2.5-14b-instruct

models-pull-34b: ## Pull a 34B int4 GGUF (Qwen2.5-32B int4).
	./scripts/download_models.sh qwen2.5-32b-instruct-q4_k_m

models-pull-70b: ## Pull a 70B int4 GGUF (Llama-3.1-70B int4).
	./scripts/download_models.sh llama-3.1-70b-instruct-q4_k_m

# -----------------------------------------------------------------------------
# Housekeeping
# -----------------------------------------------------------------------------
.PHONY: clean clean-all clean-pyc clean-data

clean-pyc: ## Remove .pyc + __pycache__.
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete

clean: clean-pyc ## Remove build artifacts but keep models + results.
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .ruff_cache/ .mypy_cache/ htmlcov/ coverage.xml .coverage

clean-data: ## DANGEROUS — remove generated benchmarks + results.
	@read -r -p "Delete data/processed and results/? [y/N] " ans && [ "$$ans" = "y" ] || (echo "aborted"; exit 1)
	rm -rf data/processed/* results/*

clean-all: clean clean-data ## Nuke everything except sources and raw data.
	rm -rf $(VENV)
