"""End-to-end API integration test for the memory bus.

Uses :class:`fastapi.testclient.TestClient` so the test does not need a real
network or uvicorn process. The compressor is the identity (no-compression)
variant so the test runs without any model weights.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from m6.compressors import make_compressor
from m6.memory_bus.api import create_app


@pytest.fixture()
def client() -> TestClient:
    app = create_app(compressor=make_compressor("none"))
    return TestClient(app)


@pytest.mark.integration()
def test_healthz(client: TestClient) -> None:
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"


@pytest.mark.integration()
def test_write_then_read_roundtrip(client: TestClient) -> None:
    payload = {
        "fragment": {
            "fragment_id": "frag-0001",
            "text": "Hello world.",
            "tags": {"acl_mask": 0, "classification": 0},
        }
    }
    r = client.post("/v1/write", json=payload)
    assert r.status_code == 201, r.text
    slot_id = r.json()["slot_id"]
    audit_rowid = r.json()["audit_rowid"]
    assert audit_rowid > 0

    r2 = client.get(f"/v1/read/{slot_id}")
    assert r2.status_code == 200
    assert r2.json()["slot"]["slot_id"] == slot_id


@pytest.mark.integration()
def test_read_denied_when_classification_below(client: TestClient) -> None:
    # Write a CONFIDENTIAL (=2) fragment. The default dev principal is super-user,
    # so we write OK. Then we attempt to read with a low-classification principal.
    payload = {
        "fragment": {
            "fragment_id": "frag-secret",
            "text": "secrets",
            "tags": {"acl_mask": 0, "classification": 2},
        }
    }
    r = client.post("/v1/write", json=payload)
    assert r.status_code == 201
    slot_id = r.json()["slot_id"]

    # Now read as a principal with classification=INTERNAL (=1).
    headers = {"X-M6-Principal": "alice:0:1"}
    r2 = client.get(f"/v1/read/{slot_id}", headers=headers)
    assert r2.status_code == 403


@pytest.mark.integration()
def test_audit_history_appears(client: TestClient) -> None:
    payload = {
        "fragment": {
            "fragment_id": "frag-history",
            "text": "log me",
            "tags": {"acl_mask": 0, "classification": 0},
        }
    }
    r = client.post("/v1/write", json=payload)
    slot_id = r.json()["slot_id"]
    client.get(f"/v1/read/{slot_id}")
    hist = client.get(f"/v1/audit/{slot_id}").json()
    # Expect a WRITE + a READ (chain hash should differ).
    event_types = {row["event_type"] for row in hist}
    assert {"WRITE", "READ"}.issubset(event_types)
