"""ACL policy enforcement.

Two surfaces:

* :class:`Principal` — the resolved requester identity. Built from a bearer
  token or a development header. Carries the ACL bitmask + classification.
* :func:`enforce` — pure predicate: given a slot's tags and a principal,
  return ``True`` iff access is permitted.

We avoid making policy a FastAPI dependency on its own; the middleware resolves
the principal once per request and stashes it on ``request.state``. The service
then calls :func:`enforce` directly.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, Request, status

from m6.memory_bus.schemas import Classification, TagVector


@dataclass(frozen=True)
class Principal:
    """Resolved requester identity."""

    subject: str
    acl_mask: int
    classification: Classification

    @classmethod
    def super_user(cls) -> Principal:
        """A god-mode principal for tests and dev mode. Never used in prod."""
        return cls(subject="dev-superuser", acl_mask=(2**64) - 1, classification=Classification.SECRET)

    @classmethod
    def from_header(cls, header: str | None) -> Principal:
        """Dev-mode parser: ``X-M6-Principal: <subject>:<acl_hex>:<class_int>``.

        Production deployments replace this with an OAuth/JWT verifier — the
        Principal surface stays the same.
        """
        if header is None or header == "":
            return cls.super_user()
        try:
            subject, acl_hex, clazz_str = header.split(":")
            acl = int(acl_hex, 16)
            clazz = Classification(int(clazz_str))
        except (ValueError, IndexError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Malformed X-M6-Principal header: {e}",
            ) from e
        if not 0 <= acl < 2**64:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="acl_mask out of uint64 range",
            )
        return cls(subject=subject, acl_mask=acl, classification=clazz)


def enforce(principal: Principal, tags: TagVector) -> bool:
    """Return True iff ``principal`` satisfies the tag's policy."""
    return tags.grants_to(principal.acl_mask, principal.classification)


def get_principal(request: Request) -> Principal:
    """FastAPI dependency: resolve the principal from ``request.state``.

    Set by :class:`PolicyMiddleware` (in ``m6.memory_bus.api``). Falling back
    to ``super_user`` here would let a misconfigured deployment bypass policy,
    so we raise instead.
    """
    principal = getattr(request.state, "principal", None)
    if principal is None:  # pragma: no cover — middleware should always set this
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Principal missing from request state — policy middleware not installed",
        )
    return principal  # type: ignore[no-any-return]
