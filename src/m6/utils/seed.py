"""Seed plumbing.

Every experiment runner calls :func:`seed_all` at the top. Returns a
:class:`Seeds` so downstream code can derive child seeds deterministically.
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Seeds:
    """Bundle of named seeds derived from a single master seed."""

    master: int
    numpy: int
    python: int
    torch: int
    workload: int

    @classmethod
    def derive(cls, master: int) -> Seeds:
        rng = random.Random(master)
        return cls(
            master=master,
            numpy=rng.randint(0, 2**31 - 1),
            python=rng.randint(0, 2**31 - 1),
            torch=rng.randint(0, 2**31 - 1),
            workload=rng.randint(0, 2**31 - 1),
        )


def seed_all(master: int) -> Seeds:
    """Seed numpy, python's ``random``, and (if installed) PyTorch.

    PyTorch and MLX are imported lazily so this module can be used without
    them installed.
    """
    seeds = Seeds.derive(master)

    random.seed(seeds.python)
    np.random.seed(seeds.numpy)
    os.environ["PYTHONHASHSEED"] = str(seeds.python)

    try:
        import torch

        torch.manual_seed(seeds.torch)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seeds.torch)
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            # MPS does not expose a seed API yet; the CPU/CUDA seeds cover us.
            pass
    except ImportError:  # pragma: no cover - optional
        pass

    try:
        import mlx.core as mx  # type: ignore[import-not-found]

        mx.random.seed(seeds.torch)
    except ImportError:  # pragma: no cover - optional, mac-only
        pass

    return seeds
