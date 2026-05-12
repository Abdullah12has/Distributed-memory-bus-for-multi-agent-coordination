"""FastAPI app factory for the memory bus reference service.

Exposes the four endpoints documented in
``docs/TECHNICAL_REFERENCE.md`` §2.1:

* ``POST /v1/write``         — compress + store + audit.
* ``GET  /v1/read/{slot_id}`` — policy-checked read.
* ``POST /v1/subscribe``     — SSE stream over the bus.
* ``GET  /v1/audit/{slot_id}`` — provenance chain.

Plus operational endpoints:

* ``GET  /healthz`` — liveness + audit chain tip.
* ``GET  /docs``    — auto-generated OpenAPI UI.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import Depends, FastAPI, HTTPException, Path, Request, status
from fastapi.responses import StreamingResponse

from m6 import __version__
from m6.config.logging import configure_logging, get_logger
from m6.config.settings import M6Settings, get_settings
from m6.memory_bus.policy import Principal, get_principal
from m6.memory_bus.schemas import (
    AuditRow,
    CompressedSlot,
    HealthResponse,
    ReadResponse,
    SlotId,
    SubscribeRequest,
    WriteRequest,
    WriteResponse,
)
from m6.memory_bus.service import (
    CompressorAPI,
    MemoryBusService,
    PolicyDenied,
    SlotNotFound,
)
from m6.memory_bus.storage import (
    FaissVectorStore,
    InMemoryScratchpad,
    SQLiteAuditLog,
)

if TYPE_CHECKING:
    from starlette.types import ASGIApp

log = get_logger(__name__)


# --------------------------------------------------------------------------- #
# App factory
# --------------------------------------------------------------------------- #
def create_app(
    settings: M6Settings | None = None,
    *,
    compressor: CompressorAPI | None = None,
) -> FastAPI:
    """Build a FastAPI app. ``compressor`` may be injected for tests."""
    settings = settings or get_settings()
    configure_logging(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # ---- startup ----
        audit = SQLiteAuditLog(settings.ensure(settings.db_path))
        scratchpad = InMemoryScratchpad(ttl_seconds=settings.scratchpad_ttl_seconds)
        vector_store = FaissVectorStore(settings.ensure(settings.faiss_path))

        cmp = compressor or _load_default_compressor(settings)
        service = MemoryBusService(
            audit=audit, scratchpad=scratchpad, vector_store=vector_store, compressor=cmp
        )
        app.state.service = service
        app.state.audit = audit
        log.info("api.startup", env=settings.env, version=__version__)
        try:
            yield
        finally:
            # ---- shutdown ----
            vector_store.save()
            audit.close()
            log.info("api.shutdown")

    app = FastAPI(
        title="m6 memory bus",
        version=__version__,
        description=(
            "Reference implementation of the distributed memory bus for "
            "multi-agent campus systems. See `docs/TECHNICAL_REFERENCE.md` "
            "for the full contract."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(PolicyMiddleware)

    _register_routes(app)
    _register_exception_handlers(app)

    if settings.otel_exporter_otlp_endpoint:
        _wire_otel(app, settings)

    return app


# --------------------------------------------------------------------------- #
# Middlewares
# --------------------------------------------------------------------------- #
class PolicyMiddleware:
    """Resolve the requester ``Principal`` from headers, attach to request.state.

    In production this is replaced with an OAuth/JWT verifier; the dev-mode
    header parser is documented in :class:`m6.memory_bus.policy.Principal`.
    """

    def __init__(self, app: "ASGIApp") -> None:
        self.app = app

    async def __call__(self, scope: dict[str, object], receive: object, send: object) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)  # type: ignore[arg-type]
            return
        headers = dict(scope.get("headers", []))  # type: ignore[arg-type]
        header_val = headers.get(b"x-m6-principal", b"").decode()
        principal = Principal.from_header(header_val or None)
        # Starlette stuffs request.state into scope["state"] when using FastAPI.
        scope.setdefault("state", {})
        scope["state"]["principal"] = principal  # type: ignore[index]
        await self.app(scope, receive, send)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
def _register_routes(app: FastAPI) -> None:
    @app.get("/healthz", response_model=HealthResponse, tags=["ops"])
    async def healthz(request: Request) -> HealthResponse:
        settings = get_settings()
        audit = request.app.state.audit
        tip = audit.chain_tip()
        return HealthResponse(
            version=__version__, env=settings.env, audit_chain_tip=tip.hex() if tip else None
        )

    @app.post("/v1/write", response_model=WriteResponse, tags=["bus"], status_code=status.HTTP_201_CREATED)
    async def write(
        request: Request,
        body: WriteRequest,
        principal: Principal = Depends(get_principal),
    ) -> WriteResponse:
        service: MemoryBusService = request.app.state.service
        return service.write(
            principal=principal, fragment=body.fragment, target_ratio=body.target_ratio
        )

    @app.get("/v1/read/{slot_id}", response_model=ReadResponse, tags=["bus"])
    async def read(
        request: Request,
        slot_id: SlotId = Path(..., description="Slot id returned from /v1/write"),
        principal: Principal = Depends(get_principal),
    ) -> ReadResponse:
        service: MemoryBusService = request.app.state.service
        slot, row = service.read(principal, slot_id)
        return ReadResponse(slot=slot, audit_rowid=row.rowid)

    @app.get("/v1/audit/{slot_id}", response_model=list[AuditRow], tags=["bus"])
    async def audit_history(
        request: Request,
        slot_id: SlotId = Path(..., description="Slot id to look up"),
    ) -> list[AuditRow]:
        service: MemoryBusService = request.app.state.service
        return service.audit_history(slot_id)

    @app.post("/v1/subscribe", tags=["bus"])
    async def subscribe(
        request: Request,
        body: SubscribeRequest,
        principal: Principal = Depends(get_principal),
    ) -> StreamingResponse:
        """Stream new slot ids matching ``body.query`` via SSE.

        The reference implementation is a simple poll-and-forward loop: every
        second it re-runs the vector search and emits any newly-matched slot
        ids. Production deployments substitute a notify-based path (Postgres
        ``LISTEN/NOTIFY`` or NATS subscription).
        """
        service: MemoryBusService = request.app.state.service

        async def event_source() -> AsyncIterator[bytes]:
            seen: set[str] = set()
            for _ in range(body.ttl_seconds):
                # The embed step requires a Compressor that supports text
                # embedding. We delegate that to the underlying compressor's
                # `embed_text` capability and skip if missing.
                emb = getattr(service.compressor, "embed_text", None)
                if emb is None:
                    yield b"event: error\ndata: compressor lacks embed_text\n\n"
                    return
                q = emb(body.query)
                hits = service.vector_store.search(q, k=body.k)
                for slot_id, score in hits:
                    if slot_id in seen:
                        continue
                    # Re-check the policy at emit time — tags could have
                    # changed between indexing and now.
                    slot = service.scratchpad.get(slot_id)
                    if slot is None or not slot.tags.grants_to(
                        principal.acl_mask, principal.classification
                    ):
                        continue
                    seen.add(slot_id)
                    payload = json.dumps({"slot_id": slot_id, "score": score})
                    yield f"data: {payload}\n\n".encode("utf-8")
                await asyncio.sleep(1.0)

        return StreamingResponse(event_source(), media_type="text/event-stream")


# --------------------------------------------------------------------------- #
# Error mapping
# --------------------------------------------------------------------------- #
def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(PolicyDenied)
    async def policy_denied(_request: Request, exc: PolicyDenied) -> StreamingResponse:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    @app.exception_handler(SlotNotFound)
    async def slot_not_found(_request: Request, exc: SlotNotFound) -> StreamingResponse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# --------------------------------------------------------------------------- #
# Dependency wiring
# --------------------------------------------------------------------------- #
def _load_default_compressor(settings: M6Settings) -> CompressorAPI:
    """Build the default compressor by name.

    Imports the compressors subpackage **lazily** so a bare ``import m6`` does
    not drag PyTorch/MLX/sentence-transformers into the process.
    """
    from m6.compressors import make_compressor

    return make_compressor(settings.default_compressor, target_ratio=settings.default_ratio)  # type: ignore[return-value]


def _wire_otel(app: FastAPI, settings: M6Settings) -> None:
    """Wire OpenTelemetry instrumentation if an endpoint is configured."""
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:  # pragma: no cover
        log.warning("otel.import_failed")
        return

    provider = TracerProvider(
        resource=Resource.create({"service.name": settings.otel_service_name})
    )
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint))
    )
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)


# The default app importable as `m6.memory_bus.api:app`.
app: FastAPI = create_app()
