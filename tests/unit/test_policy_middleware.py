"""PolicyMiddleware → request.state.principal regression test.

This test pins the fix from code-review issue #1: setting scope["state"] to a
dict (instead of a Starlette ``State()``) silently breaks every downstream
``request.state.<attr>`` access. The integration test below would fail with
404/500 if the bug is reintroduced.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from m6.memory_bus.api import PolicyMiddleware
from m6.memory_bus.policy import Principal


@pytest.fixture()
def app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(PolicyMiddleware)

    @app.get("/whoami")
    def whoami(request: Request) -> dict[str, object]:
        principal = request.state.principal
        return {"subject": principal.subject, "acl": principal.acl_mask}

    return app


@pytest.mark.integration()
def test_no_header_yields_superuser(app: FastAPI) -> None:
    """Without X-M6-Principal, dev-mode super-user is set on request.state."""
    client = TestClient(app)
    r = client.get("/whoami")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["subject"] == "dev-superuser"
    # super-user has every bit set.
    assert body["acl"] == (2**64) - 1


@pytest.mark.integration()
def test_header_resolves_to_principal(app: FastAPI) -> None:
    headers = {"X-M6-Principal": "alice:0xff:2"}
    client = TestClient(app)
    r = client.get("/whoami", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["subject"] == "alice"
    assert body["acl"] == 0xFF


def test_principal_attribute_access_works_on_state() -> None:
    """Unit-level guard: Principal.from_header is callable + attribute access works."""
    p = Principal.from_header("bob:0x01:1")
    assert p.subject == "bob"
    assert p.acl_mask == 1
    assert int(p.classification) == 1
