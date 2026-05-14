"""Metric implementations.

One module per family per plan §5.2. Each module exposes pure functions of
their inputs: no model state, no IO, no side effects beyond logging.
"""

from m6.evaluation.metrics.coordination import (
    CoordinationMetrics,
    score_coordination_trace,
)
from m6.evaluation.metrics.qa import em_score, f1_score, rouge_l
from m6.evaluation.metrics.tag_preservation import preservation_rate

__all__ = [
    "CoordinationMetrics",
    "em_score",
    "f1_score",
    "preservation_rate",
    "rouge_l",
    "score_coordination_trace",
]
