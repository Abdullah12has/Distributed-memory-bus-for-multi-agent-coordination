"""Pin the LLMLingua-2 device-resolution regression.

The original code passed ``device="auto"`` straight through to the upstream
``llmlingua.PromptCompressor``, which on Apple Silicon crashed with
``"Torch not compiled with CUDA enabled"`` because ``transformers`` defaults
to a ``"cuda"`` device map when none is specified. The fix is to resolve
``"auto"`` ourselves to CUDA / MPS / CPU based on what PyTorch reports as
available. These tests pin the resolution table.
"""

from __future__ import annotations

from unittest.mock import patch

from m6.compressors.lingua2 import LLMLingua2Compressor


def test_resolve_explicit_device_passes_through() -> None:
    """Anything other than 'auto' is honoured as-is."""
    assert LLMLingua2Compressor._resolve_device("cpu") == "cpu"
    assert LLMLingua2Compressor._resolve_device("mps") == "mps"
    assert LLMLingua2Compressor._resolve_device("cuda") == "cuda"
    assert LLMLingua2Compressor._resolve_device("cuda:0") == "cuda:0"


def test_auto_prefers_cuda_when_available() -> None:
    """If CUDA is reported available, resolve to 'cuda'."""
    with patch("torch.cuda.is_available", return_value=True):
        assert LLMLingua2Compressor._resolve_device("auto") == "cuda"


def test_auto_falls_back_to_mps_on_apple_silicon() -> None:
    """No CUDA but MPS available → 'mps' (the M-series case)."""

    class FakeMPS:
        @staticmethod
        def is_available() -> bool:
            return True

    with (
        patch("torch.cuda.is_available", return_value=False),
        patch("torch.backends.mps", FakeMPS),
    ):
        assert LLMLingua2Compressor._resolve_device("auto") == "mps"


def test_auto_falls_back_to_cpu_when_no_accelerator() -> None:
    """No CUDA, no MPS → 'cpu' (CI / Linux without GPU)."""

    class NoMPS:
        @staticmethod
        def is_available() -> bool:
            return False

    with (
        patch("torch.cuda.is_available", return_value=False),
        patch("torch.backends.mps", NoMPS),
    ):
        assert LLMLingua2Compressor._resolve_device("auto") == "cpu"
