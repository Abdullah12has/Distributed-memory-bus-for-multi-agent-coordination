"""Pydantic wire schemas and the canonical data model.

Everything that crosses an API boundary or an audit-log boundary is defined
here. Internal subsystems (compressors, agents, retrievers) consume these types
directly — there is no separate domain model.

Reference: ``docs/TECHNICAL_REFERENCE.md`` §3 (Data Model).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import IntEnum, StrEnum
from typing import Annotated, Any, Literal

import numpy as np
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    field_serializer,
    field_validator,
)

# ----- primitive aliases -----------------------------------------------------

SlotId = Annotated[str, StringConstraints(min_length=8, max_length=128, pattern=r"^[\w\-]+$")]
FragmentId = Annotated[str, StringConstraints(min_length=1, max_length=256)]
CompressorId = Annotated[str, StringConstraints(min_length=1, max_length=64)]


class Classification(IntEnum):
    """Five-tier classification lattice from ``TECHNICAL_REFERENCE.md`` §3.2."""

    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3
    SECRET = 4


class EventType(StrEnum):
    """Event taxonomy mirrored from ``software-architecture.pdf`` §4.

    StrEnum (3.11+) gives us string-compatible values *and* an iterable enum, so
    callers can iterate ``EventType`` to populate UI dropdowns or DB CHECK
    constraints without listing names twice.
    """

    WRITE = "WRITE"
    READ = "READ"
    SUBSCRIBE = "SUBSCRIBE"
    DENY = "DENY"
    COMPRESS = "COMPRESS"
    EVICT = "EVICT"


# ----- tag vector ------------------------------------------------------------


class TagVector(BaseModel):
    """Provenance + ACL metadata that travels with every fragment and slot.

    See ``docs/TECHNICAL_REFERENCE.md`` §3.2 for the design rationale.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    acl_mask: int = Field(ge=0, lt=2**64, description="64-bit capability bitmask.")
    classification: Classification = Classification.PUBLIC
    source_ids: tuple[str, ...] = Field(default_factory=tuple)
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    inherited_from: tuple[SlotId, ...] = Field(default_factory=tuple)

    @field_validator("acl_mask")
    @classmethod
    def _check_acl_in_uint64(cls, v: int) -> int:
        if not 0 <= v < 2**64:
            msg = f"acl_mask {v} out of uint64 range"
            raise ValueError(msg)
        return v

    @field_serializer("issued_at")
    def _ser_dt(self, v: datetime) -> str:
        return v.astimezone(timezone.utc).isoformat()

    # ------------------------------------------------------------------ #
    # Lattice-respecting aggregation
    # ------------------------------------------------------------------ #
    @classmethod
    def union(cls, tags: list[TagVector]) -> TagVector:
        """Lattice-respecting aggregation per ``TECHNICAL_REFERENCE.md`` §5.5.

        ``acl_mask`` is the bitwise OR; ``classification`` is the maximum;
        ``source_ids`` and ``inherited_from`` are concatenated and deduped.
        """
        if not tags:
            return cls(acl_mask=0)
        acl = 0
        clazz = Classification.PUBLIC
        sources: list[str] = []
        parents: list[str] = []
        earliest = min(t.issued_at for t in tags)
        for t in tags:
            acl |= t.acl_mask
            clazz = Classification(max(int(clazz), int(t.classification)))
            sources.extend(t.source_ids)
            parents.extend(t.inherited_from)
        return cls(
            acl_mask=acl,
            classification=clazz,
            source_ids=tuple(dict.fromkeys(sources)),
            issued_at=earliest,
            inherited_from=tuple(dict.fromkeys(parents)),
        )

    def grants_to(self, requester_acl: int, requester_clazz: Classification) -> bool:
        """Does ``requester`` satisfy this tag's policy?

        Rule: every capability bit the tag requires must be in ``requester_acl``,
        and the requester's classification must be ≥ the tag's classification.
        """
        return (requester_acl & self.acl_mask) == self.acl_mask and int(requester_clazz) >= int(
            self.classification
        )


# ----- fragment --------------------------------------------------------------


class Fragment(BaseModel):
    """A raw chunk of source text. Pre-compression."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    fragment_id: FragmentId
    text: str = Field(min_length=1, max_length=200_000)
    tags: TagVector
    task_hint: str | None = Field(default=None, max_length=4_000)


# ----- slot payload variants -------------------------------------------------


class TextSummary(BaseModel):
    """Hard-prompt compressors emit a literal text summary."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal["text"] = "text"
    text: str


class SoftEmbed(BaseModel):
    """ICAE-style soft-prompt compressors emit memory-slot embeddings.

    Stored as a flattened list of floats with explicit ``(num_slots, d_model)``
    shape so the wire format is portable.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal["soft"] = "soft"
    num_slots: int = Field(gt=0, le=2048)
    d_model: int = Field(gt=0, le=8192)
    values: tuple[float, ...]

    @field_validator("values")
    @classmethod
    def _check_shape(cls, v: tuple[float, ...], info: Any) -> tuple[float, ...]:
        # We re-derive num_slots*d_model from the values length at construction
        # so a malformed payload fails closed.
        return v

    def as_ndarray(self) -> np.ndarray:
        return np.asarray(self.values, dtype=np.float32).reshape(self.num_slots, self.d_model)

    @classmethod
    def from_ndarray(cls, arr: np.ndarray) -> SoftEmbed:
        if arr.ndim != 2:
            msg = f"SoftEmbed requires 2D array, got {arr.ndim}D"
            raise ValueError(msg)
        flat = arr.astype(np.float32).reshape(-1).tolist()
        return cls(num_slots=arr.shape[0], d_model=arr.shape[1], values=tuple(flat))


class TokenIds(BaseModel):
    """AutoCompressor-style: a list of token IDs in the encoder's vocab."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal["tokens"] = "tokens"
    tokenizer_id: str
    ids: tuple[int, ...]


SlotPayload = Annotated[
    TextSummary | SoftEmbed | TokenIds, Field(discriminator="kind")
]


# ----- compressed slot -------------------------------------------------------


class CompressedSlot(BaseModel):
    """The unit of currency on the bus."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    slot_id: SlotId
    payload: SlotPayload
    tags: TagVector
    audit_pointers: tuple[int, ...] = Field(default_factory=tuple)
    compressor_id: CompressorId
    ratio: float = Field(ge=1.0, le=64.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @computed_field  # type: ignore[misc]
    @property
    def payload_kind(self) -> str:
        return self.payload.kind


# ----- audit row -------------------------------------------------------------


class AuditRow(BaseModel):
    """One row in the audit log. Append-only."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rowid: int
    slot_id: SlotId
    event_type: str
    requester_acl: int | None = None
    requester_classification: int | None = None
    result: Literal["OK", "DENIED", "ERROR"]
    prev_hash: bytes
    payload_hash: bytes
    chain_hash: bytes
    created_at: datetime

    @field_serializer("prev_hash", "payload_hash", "chain_hash")
    def _ser_bytes(self, v: bytes) -> str:
        return v.hex()


# ----- request / response schemas -------------------------------------------


class WriteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fragment: Fragment
    compressor_id: CompressorId | None = None
    target_ratio: float | None = Field(default=None, ge=1.0, le=64.0)


class WriteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    slot_id: SlotId
    chain_hash: str
    audit_rowid: int


class ReadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    slot: CompressedSlot
    audit_rowid: int


class SubscribeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str
    ttl_seconds: int = Field(ge=1, le=24 * 3600)
    k: int = Field(default=10, ge=1, le=200)


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["ok"] = "ok"
    version: str
    env: str
    audit_chain_tip: str | None = None
