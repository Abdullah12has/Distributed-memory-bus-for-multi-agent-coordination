"""Loss primitives for the ICAE-style dual-objective trainer.

The trainer composes::

    L = L_recon + λ_NCE · L_NCE  (+ λ_tag · L_tag for C4)

* ``L_recon`` — standard token-level CE on the source fragment, computed
  over the frozen decoder given the compressed [MEM] slots.
* ``L_NCE`` — InfoNCE over (positive, negative) source-fragment pairs.

MLX does not ship a batch contrastive primitive (as of 0.21). We implement
``L_NCE`` manually as a cross-entropy over a `(B, B)` similarity matrix.
``_probe_mlx_nce`` runs the same trick on MLX to fail fast if a runtime
change breaks it.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np


def infonce_loss(
    anchors: Any,  # torch.Tensor or mx.array, shape (B, D)
    positives: Any,
    *,
    temperature: float = 0.07,
    backend: str = "auto",
) -> Any:
    """Symmetric InfoNCE.

    Both directions of the contrastive loss are computed and averaged. This is
    the SimCLR formulation; the temperature default 0.07 matches the original
    SimCLR paper.

    ``backend="auto"`` picks torch if both tensors are torch tensors, mlx if
    both are mlx arrays.
    """
    if backend == "auto":
        backend = _detect_backend(anchors)

    if backend == "torch":
        return _infonce_torch(anchors, positives, temperature=temperature)
    if backend == "mlx":
        return _infonce_mlx(anchors, positives, temperature=temperature)
    msg = f"Unknown backend {backend!r}"
    raise ValueError(msg)


# --------------------------------------------------------------------------- #
# Torch backend
# --------------------------------------------------------------------------- #
def _infonce_torch(anchors: Any, positives: Any, *, temperature: float) -> Any:
    import torch
    import torch.nn.functional as F

    a = F.normalize(anchors, dim=-1)
    p = F.normalize(positives, dim=-1)
    sim = (a @ p.T) / temperature  # (B, B)
    labels = torch.arange(sim.size(0), device=sim.device)
    loss_a = F.cross_entropy(sim, labels)
    loss_b = F.cross_entropy(sim.T, labels)
    return 0.5 * (loss_a + loss_b)


# --------------------------------------------------------------------------- #
# MLX backend
# --------------------------------------------------------------------------- #
def _infonce_mlx(anchors: Any, positives: Any, *, temperature: float) -> Any:
    import mlx.core as mx
    from mlx import nn

    def _l2(x: Any) -> Any:
        n = mx.sqrt(mx.sum(x * x, axis=-1, keepdims=True) + 1e-12)
        return x / n

    a = _l2(anchors)
    p = _l2(positives)
    sim = (a @ mx.transpose(p)) / temperature
    n = sim.shape[0]
    labels = mx.arange(n)
    loss_a = nn.losses.cross_entropy(sim, labels, reduction="mean")
    loss_b = nn.losses.cross_entropy(mx.transpose(sim), labels, reduction="mean")
    return 0.5 * (loss_a + loss_b)


def _detect_backend(x: Any) -> str:
    cls_module = type(x).__module__
    if cls_module.startswith("torch"):
        return "torch"
    if cls_module.startswith("mlx"):
        return "mlx"
    msg = f"Cannot detect backend for {type(x).__name__}"
    raise TypeError(msg)


# --------------------------------------------------------------------------- #
# Numpy reference implementation for unit tests
# --------------------------------------------------------------------------- #
def _infonce_numpy(
    anchors: np.ndarray, positives: np.ndarray, *, temperature: float = 0.07
) -> float:
    """Reference impl. Tests assert torch and mlx match this."""
    a = anchors / (np.linalg.norm(anchors, axis=-1, keepdims=True) + 1e-12)
    p = positives / (np.linalg.norm(positives, axis=-1, keepdims=True) + 1e-12)
    sim = (a @ p.T) / temperature

    def _ce(s: np.ndarray) -> float:
        # Numerically stable log-softmax cross-entropy with label = i.
        m = s.max(axis=1, keepdims=True)
        ls = s - m - np.log(np.exp(s - m).sum(axis=1, keepdims=True))
        return float(-np.diag(ls).mean())

    return 0.5 * (_ce(sim) + _ce(sim.T))


def _probe_mlx_nce() -> bool:
    """Run a 3×3 InfoNCE on MLX. Returns True iff MLX produces a finite scalar.

    Called at trainer start-up; if False, the trainer falls back to PyTorch-MPS
    automatically (plan risk register: "MLX lacks an InfoNCE-friendly batch
    contrastive primitive").
    """
    try:
        import mlx.core as mx

        a = mx.random.normal(shape=(3, 8))
        p = mx.random.normal(shape=(3, 8))
        loss = _infonce_mlx(a, p, temperature=0.07)
        val = float(loss)
        return math.isfinite(val)
    except Exception:
        return False
