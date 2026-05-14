"""Compressor training utilities.

Public surface deliberately minimal: callers import the trainer entry-point
from :mod:`m6.compressors.training.train_icae` and the loss primitives from
:mod:`m6.compressors.training.loss`. The dataset loaders for the H3 ablation
(QA vs. dialogue) live in :mod:`m6.compressors.training.dataset`.
"""

from m6.compressors.training.dataset import DialogueDataset, QADataset
from m6.compressors.training.loss import infonce_loss

__all__ = ["DialogueDataset", "QADataset", "infonce_loss"]
