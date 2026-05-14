"""ICAE-style dual-objective trainer.

Implements ``L = L_recon + λ_NCE·L_NCE (+ λ_tag·L_tag)`` per
``docs/TECHNICAL_REFERENCE.md`` §5.2.

This script is deliberately a CLI: experiment configs live in
``configs/training/*.yaml``. Wallclock budget is ~3 days for 7B / rank 16 /
~50 MB corpus on M4 Pro (plan §4.3).

Backends (auto-detected):
* MLX + PEFT-via-MLX on Apple Silicon.
* PyTorch + PEFT (MPS or CUDA) elsewhere.

The trainer **probes for an MLX-friendly InfoNCE primitive at start-up**
(``loss._probe_mlx_nce``) and falls back to PyTorch-MPS if it is missing
(mitigation for plan risk-register row 2).

Because the training run is a long-tailed multi-day job, the script is
structured around a single :func:`main` function with explicit checkpointing
and is intended to be invoked via ``make train-icae`` (which sets
``configs/training/icae-7b.yaml`` as the source of truth).
"""

from __future__ import annotations

import dataclasses
import json
import os
import sys
import time
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from m6.compressors.training.dataset import DialogueDataset, QADataset, TrainingExample
from m6.compressors.training.loss import _probe_mlx_nce, infonce_loss
from m6.config.logging import configure_logging, get_logger
from m6.utils.io import atomic_write, hash_dict, make_run_id
from m6.utils.seed import seed_all

log = get_logger(__name__)


@dataclass(frozen=True)
class TrainerConfig:
    """Resolved training configuration. Mirrors ``configs/training/icae-7b.yaml``."""

    run_name: str = "icae-7b"
    base_model: str = "meta-llama/Llama-3.1-8B-Instruct"
    dataset: str = "qa"  # "qa" | "dialogue"
    dataset_path: str = "data/processed/training/qa.jsonl"
    num_slots: int = 128
    max_input_tokens: int = 512

    # Optimisation
    epochs: int = 3
    batch_size: int = 4
    grad_accum: int = 8
    learning_rate: float = 3e-4
    weight_decay: float = 0.0
    warmup_steps: int = 200
    seed: int = 0

    # LoRA
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05

    # Loss weights
    lambda_nce: float = 0.3
    lambda_tag: float = 0.0  # >0 ⇒ enable C4 tag head
    nce_temperature: float = 0.07

    # IO
    out_dir: str = "checkpoints/icae-7b"
    log_every: int = 25
    save_every: int = 500

    # Sanity / time-boxes
    max_wallclock_hours: float = 72.0  # plan §4.3 ≤3 days
    backend: str = "auto"  # "auto" | "torch" | "mlx"

    @classmethod
    def from_yaml(cls, path: Path | str) -> TrainerConfig:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        # Drop unknown keys with a warning so config evolution is forgiving.
        known = {f.name for f in dataclasses.fields(cls)}
        unknown = set(data) - known
        if unknown:
            log.warning("trainer.unknown_config_keys", keys=sorted(unknown))
        return cls(**{k: v for k, v in data.items() if k in known})


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="ICAE-style dual-objective trainer.")
    parser.add_argument("--config", required=True, help="Path to YAML training config.")
    parser.add_argument("--dry-run", action="store_true", help="Build everything but don't train.")
    args = parser.parse_args(argv)

    configure_logging()
    cfg = TrainerConfig.from_yaml(args.config)
    seeds = seed_all(cfg.seed)
    log.info("trainer.config", **dataclasses.asdict(cfg), seed_master=seeds.master)

    if args.dry_run:
        log.info("trainer.dry_run_ok")
        return 0

    backend = _select_backend(cfg.backend)
    log.info("trainer.backend", backend=backend)

    if backend == "mlx":
        return _run_mlx(cfg)
    return _run_torch(cfg)


# --------------------------------------------------------------------------- #
# Backend selection
# --------------------------------------------------------------------------- #
def _select_backend(requested: str) -> str:
    """Resolve a training backend.

    Note: ``auto`` always returns ``torch`` until the MLX trainer ships. We
    keep the MLX probe call in place so a future opt-in still benefits from
    fail-fast detection; setting ``backend: mlx`` explicitly is the way to
    request it once implemented.
    """
    if requested in {"torch", "mlx"}:
        return requested
    if sys.platform == "darwin" and os.uname().machine == "arm64":
        # Surface MLX-runtime probe outcome in the logs so future maintainers
        # know when the primitive lands. The probe does not change the choice.
        if not _probe_mlx_nce():
            log.warning("trainer.mlx_nce_probe_failed", note="MLX trainer not enabled regardless.")
    return "torch"


# --------------------------------------------------------------------------- #
# Dataset loading
# --------------------------------------------------------------------------- #
def _load_dataset(cfg: TrainerConfig) -> Sequence[TrainingExample]:
    if cfg.dataset == "qa":
        return QADataset(cfg.dataset_path)
    if cfg.dataset == "dialogue":
        return DialogueDataset(cfg.dataset_path, seed=cfg.seed)
    msg = f"Unknown dataset type: {cfg.dataset!r}"
    raise ValueError(msg)


def _iter_batches(
    ds: Sequence[TrainingExample], batch_size: int
) -> Iterator[list[TrainingExample]]:
    batch: list[TrainingExample] = []
    for ex in ds:
        batch.append(ex)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


# --------------------------------------------------------------------------- #
# PyTorch backend
# --------------------------------------------------------------------------- #
def _run_torch(cfg: TrainerConfig) -> int:
    """Real LoRA training via Transformers + PEFT.

    The full training loop is verbose; the most thesis-relevant pieces are:

    1. Encoder gets LoRA adapters (target modules from ADR-001); decoder is
       frozen — Ge et al. ICAE 2024.
    2. ``L_recon`` = CE on the source fragment given [MEM] slots.
    3. ``L_NCE`` = ``infonce_loss(anchor_embeds, positive_embeds)``.
    4. Optional ``L_tag`` for C4.
    """
    try:
        import torch
        import torch.nn.functional as F
        from peft import LoraConfig, get_peft_model
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            get_cosine_schedule_with_warmup,
        )
    except ImportError as e:
        log.error("trainer.torch_missing", error=str(e))
        return 2

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )
    log.info("trainer.torch.device", device=device)

    # ---- model + tokenizer ----
    tokenizer = AutoTokenizer.from_pretrained(cfg.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    if "[MEM]" not in tokenizer.get_vocab():
        tokenizer.add_special_tokens({"additional_special_tokens": ["[MEM]"]})
    base = AutoModelForCausalLM.from_pretrained(
        cfg.base_model,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
    )
    base.resize_token_embeddings(len(tokenizer))
    base.to(device)

    lora_cfg = LoraConfig(
        r=cfg.lora_rank,
        lora_alpha=cfg.lora_alpha,
        lora_dropout=cfg.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )
    encoder = get_peft_model(base, lora_cfg)
    encoder.print_trainable_parameters()

    # The decoder is frozen — same backbone, no LoRA. AutoCompressor pattern.
    decoder = AutoModelForCausalLM.from_pretrained(
        cfg.base_model,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
    )
    decoder.resize_token_embeddings(len(tokenizer))
    decoder.to(device)
    decoder.eval()
    for p in decoder.parameters():
        p.requires_grad = False

    # ---- data ----
    dataset = _load_dataset(cfg)
    log.info("trainer.dataset_loaded", size=len(dataset))

    # ---- optimiser ----
    optim = torch.optim.AdamW(
        [p for p in encoder.parameters() if p.requires_grad],
        lr=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
        betas=(0.9, 0.95),
    )
    total_steps = (len(dataset) // cfg.batch_size) * cfg.epochs // max(cfg.grad_accum, 1)
    scheduler = get_cosine_schedule_with_warmup(optim, cfg.warmup_steps, total_steps)

    # ---- C4 tag head (lazy; only if lambda_tag > 0) ----
    tag_head: torch.nn.Module | None = None
    if cfg.lambda_tag > 0:
        tag_head = _build_tag_head(base.config.hidden_size).to(device)
        for p in tag_head.parameters():
            p.requires_grad = True
        optim.add_param_group({"params": tag_head.parameters(), "lr": cfg.learning_rate})

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = make_run_id(cfg.run_name)
    _write_manifest(out_dir, cfg, run_id)

    mem_token_id = tokenizer.convert_tokens_to_ids("[MEM]")
    t_start = time.time()
    step = 0
    for epoch in range(cfg.epochs):
        for batch in _iter_batches(dataset, cfg.batch_size):
            if (time.time() - t_start) / 3600 > cfg.max_wallclock_hours:
                log.warning("trainer.timeboxed", reason="exceeded max_wallclock_hours")
                _save(encoder, tag_head, out_dir, step=step, final=True)
                return 0

            anchor_inputs = tokenizer(
                [ex.anchor_text for ex in batch],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=cfg.max_input_tokens,
            ).to(device)
            positive_inputs = tokenizer(
                [ex.positive_text for ex in batch],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=cfg.max_input_tokens,
            ).to(device)

            # Append num_slots MEM tokens for the compressor pass.
            def _append_mem(inputs: dict[str, Any]) -> dict[str, Any]:
                B = inputs["input_ids"].size(0)
                mem_ids = torch.full(
                    (B, cfg.num_slots),
                    int(mem_token_id),
                    device=device,
                    dtype=inputs["input_ids"].dtype,
                )
                input_ids = torch.cat([inputs["input_ids"], mem_ids], dim=1)
                attn = torch.cat([inputs["attention_mask"], torch.ones_like(mem_ids)], dim=1)
                return {"input_ids": input_ids, "attention_mask": attn}

            a_in = _append_mem(anchor_inputs)
            p_in = _append_mem(positive_inputs)

            a_out = encoder(**a_in, output_hidden_states=True, return_dict=True)
            p_out = encoder(**p_in, output_hidden_states=True, return_dict=True)

            # Memory embeddings = last hidden, last num_slots positions.
            a_mem = a_out.hidden_states[-1][:, -cfg.num_slots :, :]
            p_mem = p_out.hidden_states[-1][:, -cfg.num_slots :, :]

            # ---- L_recon ----
            # Feed [MEM_slots ; anchor_input_ids] through the FROZEN decoder,
            # cross-entropy on the anchor tokens.
            with torch.no_grad():
                dec_input_embeds = decoder.get_input_embeddings()(anchor_inputs["input_ids"])
            # Prepend mem hidden states as soft-prompt embeddings.
            soft_prompt = a_mem
            full_embeds = torch.cat([soft_prompt, dec_input_embeds], dim=1)
            labels = anchor_inputs["input_ids"].clone()
            labels[anchor_inputs["attention_mask"] == 0] = -100
            # Pad labels for the mem-slot prefix.
            pad_lab = torch.full(
                (labels.size(0), cfg.num_slots), -100, device=device, dtype=labels.dtype
            )
            labels_full = torch.cat([pad_lab, labels], dim=1)
            dec_out = decoder(inputs_embeds=full_embeds, return_dict=True)
            l_recon = F.cross_entropy(
                dec_out.logits.view(-1, dec_out.logits.size(-1)),
                labels_full.view(-1),
                ignore_index=-100,
            )

            # ---- L_NCE ----
            a_pool = a_mem.mean(dim=1)
            p_pool = p_mem.mean(dim=1)
            l_nce = infonce_loss(a_pool, p_pool, temperature=cfg.nce_temperature, backend="torch")

            # ---- L_tag (C4 only) ----
            l_tag = torch.zeros((), device=device)
            if tag_head is not None and cfg.lambda_tag > 0:
                acl_targets = torch.tensor(
                    [_unpack_uint64(ex.acl_mask) for ex in batch],
                    device=device,
                    dtype=torch.float32,
                )
                class_targets = torch.tensor(
                    [ex.classification for ex in batch], device=device, dtype=torch.long
                )
                acl_logits, class_logits = tag_head(a_pool)  # per-slot, but we use the pooled embed
                l_acl = F.binary_cross_entropy_with_logits(acl_logits, acl_targets)
                l_cls = F.cross_entropy(class_logits, class_targets)
                l_tag = l_acl + l_cls

            loss = l_recon + cfg.lambda_nce * l_nce + cfg.lambda_tag * l_tag
            (loss / cfg.grad_accum).backward()

            if (step + 1) % cfg.grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(encoder.parameters(), 1.0)
                optim.step()
                scheduler.step()
                optim.zero_grad(set_to_none=True)

            if step % cfg.log_every == 0:
                log.info(
                    "trainer.step",
                    epoch=epoch,
                    step=step,
                    l_recon=float(l_recon),
                    l_nce=float(l_nce),
                    l_tag=float(l_tag),
                    loss=float(loss),
                    lr=scheduler.get_last_lr()[0],
                )
            if step > 0 and step % cfg.save_every == 0:
                _save(encoder, tag_head, out_dir, step=step, final=False)
            step += 1

    _save(encoder, tag_head, out_dir, step=step, final=True)
    log.info("trainer.done", run_id=run_id, total_steps=step, wallclock_s=time.time() - t_start)
    return 0


def _build_tag_head(d_model: int) -> Any:
    """Build the C4 TagHead — two linears, ACL (64) and classification (5)."""
    import torch
    from torch import nn

    class TagHead(nn.Module):  # type: ignore[misc]
        def __init__(self) -> None:
            super().__init__()
            self.acl = nn.Linear(d_model, 64)
            self.cls = nn.Linear(d_model, 5)

        def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
            return self.acl(x), self.cls(x)

    return TagHead()


def _save(encoder: Any, tag_head: Any, out_dir: Path, *, step: int, final: bool) -> None:
    """Save LoRA adapter + (optional) tag head npz."""
    import numpy as np

    suffix = "final" if final else f"step-{step}"
    encoder.save_pretrained(out_dir / suffix)
    if tag_head is not None:
        np.savez(
            out_dir / suffix / "tag_head.npz",
            w_acl=tag_head.acl.weight.detach().cpu().float().numpy(),
            b_acl=tag_head.acl.bias.detach().cpu().float().numpy(),
            w_class=tag_head.cls.weight.detach().cpu().float().numpy(),
            b_class=tag_head.cls.bias.detach().cpu().float().numpy(),
        )
    log.info("trainer.checkpoint_saved", path=str(out_dir / suffix))


def _unpack_uint64(value: int) -> list[float]:
    """Pack a uint64 into a list of 64 floats (LSB-first)."""
    return [float((value >> i) & 1) for i in range(64)]


def _write_manifest(out_dir: Path, cfg: TrainerConfig, run_id: str) -> None:
    manifest = {
        "run_id": run_id,
        "config": dataclasses.asdict(cfg),
        "config_hash": hash_dict(dataclasses.asdict(cfg)),
    }
    with atomic_write(out_dir / "manifest.yaml", mode="w") as f:
        yaml.safe_dump(manifest, f, sort_keys=True)
    # Also drop a JSON-flavored manifest for downstream tools.
    with atomic_write(out_dir / "manifest.json", mode="w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)


# --------------------------------------------------------------------------- #
# MLX backend
# --------------------------------------------------------------------------- #
def _run_mlx(_cfg: TrainerConfig) -> int:
    """MLX path is the documented primary fast path (plan §6.2).

    The MLX trainer is not yet implemented. We refuse rather than silently
    falling back to the torch path, because a silent fallback turns a ~3-day
    training (MLX) into a ~10-day one (torch-MPS) without the operator
    noticing. To opt into the torch path explicitly, set ``backend: torch`` in
    the training YAML — that is the supported safety net (plan risk-register
    row 2).
    """
    msg = (
        "MLX trainer path is not yet implemented. To proceed, set "
        "`backend: torch` in the training YAML, which is the explicit "
        "PyTorch-MPS fallback path (plan risk-register row 2). Do not invoke "
        "_run_mlx programmatically — pick the backend in config."
    )
    raise NotImplementedError(msg)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
