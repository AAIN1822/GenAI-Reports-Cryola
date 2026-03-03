import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from starlette.responses import StreamingResponse

from app.main import app
from app.core.security import get_current_user


# ───────────────────────────────────────────────
# VALID PAYLOADS (MATCH REAL SCHEMAS)
# ───────────────────────────────────────────────

VALID_PROJECT_CREATE = {
    "account": "Nike",
    "structure": "Tee",
    "sub_brand": "SB",
    "season": "Summer",
    "region": "US",
    "project_description": "Test project",
}

# IMPORTANT:
# ProjectUpdate must receive valid fields
VALID_PROJECT_UPDATE = {
    "fsdu": {
        "image": "fsdu.png",
        "name": "Main FSDU",
        "dimensions": [
            {"name": "width", "value": 120.0},
            {"name": "height", "value": 240.0}
        ]
    },
    "color": "red"
}


MOCK_USER = {
    "id": "user_123",
    "email": "test@example.com",
}


# ───────────────────────────────────────────────
# CLIENT (CRITICAL FIX HERE)
# ───────────────────────────────────────────────

@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


# ───────────────────────────────────────────────
# AUTH OVERRIDE
# ───────────────────────────────────────────────

@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    yield
    app.dependency_overrides.clear()


# ───────────────────────────────────────────────
# SERVICE MOCKS (PATCH ROUTER IMPORTS)
# ───────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_project_services(monkeypatch):

    monkeypatch.setattr(
        "app.api.v1.routes.project.create_project",
        lambda payload, user: {"id": "p1", **payload.model_dump()},
    )

    monkeypatch.setattr(
        "app.api.v1.routes.project.fetch_all_projects",
        lambda user: [{"id": "p1"}, {"id": "p2"}],
    )

    monkeypatch.setattr(
        "app.api.v1.routes.project.v1_fetch_all_projects",
        lambda **kwargs: {
            "total": 1,
            "items": [{"id": "p1"}],
            "page": kwargs["page"],
            "page_size": kwargs["page_size"],
        },
    )

    monkeypatch.setattr(
        "app.api.v1.routes.project.update_project_details",
        lambda project_id, data, user: {"id": project_id, **data},
    )

    monkeypatch.setattr(
        "app.api.v1.routes.project.fetch_project_by_id",
        lambda project_id, user: {"id": project_id},
    )

    monkeypatch.setattr(
        "app.api.v1.routes.project.save_as",
        lambda project_id, payload, user: {"id": "new_project"},
    )

    def mock_download(project_id, user):
        def stream():
            yield b"file-content"
        return StreamingResponse(stream(), media_type="application/zip")

    monkeypatch.setattr(
        "app.api.v1.routes.project.download_project",
        mock_download,
    )


# ───────────────────────────────────────────────
# SUCCESS SCENARIOS
# ───────────────────────────────────────────────

def test_create_new_project(client):
    res = client.post("/projects/new-project", json=VALID_PROJECT_CREATE)
    assert res.status_code == 200


def test_update_project(client):
    res = client.put("/projects/p1/update", json=VALID_PROJECT_UPDATE)
    assert res.status_code == 200
    assert res.json()["message"] == "Project updated successfully"


def test_save_as_project(client):
    res = client.post("/projects/save_as/p1", json=VALID_PROJECT_CREATE)
    assert res.status_code == 200


def test_download_project_success(client):
    res = client.get("/projects/download_project/p1")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"


# ───────────────────────────────────────────────
# ERROR SCENARIOS
# ───────────────────────────────────────────────

def test_get_project_not_found(monkeypatch, client):
    monkeypatch.setattr(
        "app.api.v1.routes.project.fetch_project_by_id",
        lambda *_: (_ for _ in ()).throw(HTTPException(status_code=404)),
    )

    res = client.get("/projects/invalid-id")
    assert res.status_code == 404


def test_create_project_internal_error(monkeypatch, client):
    monkeypatch.setattr(
        "app.api.v1.routes.project.create_project",
        lambda *_: (_ for _ in ()).throw(Exception("DB error")),
    )

    res = client.post("/projects/new-project", json=VALID_PROJECT_CREATE)
    assert res.status_code == 500


def test_download_project_failure(monkeypatch, client):
    monkeypatch.setattr(
        "app.api.v1.routes.project.download_project",
        lambda *_: (_ for _ in ()).throw(Exception("Download failed")),
    )

    res = client.get("/projects/download_project/p1")
    assert res.status_code == 500


# ───────────────────────────────────────────────
# VALIDATION ERRORS
# ───────────────────────────────────────────────

def test_create_project_validation_error(client):
    res = client.post("/projects/new-project", json={})
    assert res.status_code == 422
