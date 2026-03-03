import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch

from app.main import app
import app.api.v1.routes.ai_integration as ai_routes

client = TestClient(app)


# ============================================================
# AUTH OVERRIDE (MUST MATCH ROUTER REFERENCE)
# ============================================================
@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[ai_routes.get_current_user] = lambda: {
        "id": "test-user"
    }
    yield
    app.dependency_overrides.clear()


# ============================================================
# COMMON MOCK
# ============================================================
@pytest.fixture
def mock_create_job():
    with patch("app.api.v1.routes.ai_integration.create_job_status") as mock:
        yield mock


# ============================================================
# GET /ai/colour_theme/{project_id}
# ============================================================

@patch("app.api.v1.routes.ai_integration.colour_theme_background_job")
def test_colour_theme_success(mock_bg, mock_create_job):
    res = client.get("/ai/colour_theme/p1")

    assert res.status_code == 200
    assert res.json()["data"]["status"] == "IN_PROGRESS"
    mock_create_job.assert_called_once()
    mock_bg.assert_called_once()


# ============================================================
# POST /ai/colour_theme_refinement/{project_id}
# ============================================================

@patch("app.api.v1.routes.ai_integration.colour_theme_refinement_background_job")
def test_colour_theme_refinement_success(mock_bg, mock_create_job):
    res = client.post(
        "/ai/colour_theme_refinement/p1",
        json={
            "choosen_url": "http://img/theme.png",
            "feedback_prompt": "Make it darker"
        }
    )

    assert res.status_code == 200
    mock_create_job.assert_called_once()
    mock_bg.assert_called_once()


def test_colour_theme_refinement_validation_error():
    res = client.post(
        "/ai/colour_theme_refinement/p1",
        json={"choosen_url": "http://img/theme.png"}
    )
    assert res.status_code == 422


# ============================================================
# POST /ai/graphics/{project_id}
# ============================================================

@patch("app.api.v1.routes.ai_integration.graphics_background_job")
def test_graphics_success(mock_bg, mock_create_job):
    res = client.post(
        "/ai/graphics/p1",
        json={
            "choosen_url": "http://img/graphic.png",
            "score": 8
        }
    )

    assert res.status_code == 200
    mock_create_job.assert_called_once()
    mock_bg.assert_called_once()


# ============================================================
# POST /ai/graphics_refinement/{project_id}
# ============================================================

@patch("app.api.v1.routes.ai_integration.graphics_refinement_background_job")
def test_graphics_refinement_success(mock_bg, mock_create_job):
    res = client.post(
        "/ai/graphics_refinement/p1",
        json={
            "selected_graphics_url": "http://img/graphic.png",
            "feedback_prompt": "Improve contrast"
        }
    )

    assert res.status_code == 200
    mock_create_job.assert_called_once()
    mock_bg.assert_called_once()


# ============================================================
# GET /ai/status/{job_id}
# ============================================================

@patch("app.api.v1.routes.ai_integration.fetch_status")
def test_job_status_success(mock_fetch):
    mock_fetch.return_value = {"status": "COMPLETED"}

    res = client.get("/ai/status/job123")

    assert res.status_code == 200
    assert res.json()["data"]["status"] == "COMPLETED"


@patch("app.api.v1.routes.ai_integration.fetch_status")
def test_job_status_not_found(mock_fetch):
    mock_fetch.side_effect = HTTPException(404, "Not found")

    res = client.get("/ai/status/job123")

    assert res.status_code == 404


# ============================================================
# POST /ai/product_placement/{project_id}
# ============================================================

@patch("app.api.v1.routes.ai_integration.product_background_job")
def test_product_placement_success(mock_bg, mock_create_job):
    res = client.post(
        "/ai/product_placement/p1",
        json={
            "choosen_url": "http://img/product.png",
            "score": 9
        }
    )

    assert res.status_code == 200
    mock_create_job.assert_called_once()
    mock_bg.assert_called_once()


# ============================================================
# POST /ai/product_placement_refinement/{project_id}
# ============================================================

@patch("app.api.v1.routes.ai_integration.product_refinement_background_job")
def test_product_placement_refinement_success(mock_bg, mock_create_job):
    res = client.post(
        "/ai/product_placement_refinement/p1",
        json={
            "choosen_url": "http://img/product.png",
            "feedback_prompt": "Adjust placement"
        }
    )

    assert res.status_code == 200
    mock_create_job.assert_called_once()
    mock_bg.assert_called_once()


# ============================================================
# POST /ai/feedback/{project_id}
# ============================================================

@patch("app.api.v1.routes.ai_integration.record_user_feedback")
def test_feedback_success(mock_feedback):
    mock_feedback.return_value = {"saved": True}

    res = client.post(
        "/ai/feedback/p1",
        json={
            "image_url": "http://img/result.png",
            "like": True,
            "stage": "Graphics"
        }
    )

    assert res.status_code == 200
    assert res.json()["data"]["saved"] is True


def test_feedback_validation_error():
    res = client.post(
        "/ai/feedback/p1",
        json={"image_url": "http://img/result.png"}
    )
    assert res.status_code == 422


# ============================================================
# INTERNAL SERVER ERROR (500)
# ============================================================

@patch("app.api.v1.routes.ai_integration.create_job_status")
def test_internal_server_error(mock_create):
    mock_create.side_effect = HTTPException(500, "DB down")

    res = client.get("/ai/colour_theme/p1")

    assert res.status_code == 500
