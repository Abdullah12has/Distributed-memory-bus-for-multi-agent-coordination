"""RAG pipeline catalogue (C3).

Three pipelines per ``docs/TECHNICAL_REFERENCE.md`` §7:

* :class:`Pipeline1` — compress→retrieve (storage-bounded regime).
* :class:`Pipeline2` — retrieve→compress (accuracy-bounded regime; LongLLMLingua).
* :class:`Pipeline3` — joint, conditional compression on retrieval relevance.

Plus the cost model in :mod:`m6.pipelines.cost_model` and a small retriever
abstraction in :mod:`m6.pipelines.retriever`.
"""

from m6.pipelines.cost_model import PRICING, PricePerMillion, eur_for_call
from m6.pipelines.p1_compress_retrieve import Pipeline1
from m6.pipelines.p2_retrieve_compress import Pipeline2
from m6.pipelines.p3_joint import Pipeline3
from m6.pipelines.retriever import RetrievedDoc, Retriever

__all__ = [
    "PRICING",
    "Pipeline1",
    "Pipeline2",
    "Pipeline3",
    "PricePerMillion",
    "RetrievedDoc",
    "Retriever",
    "eur_for_call",
]
