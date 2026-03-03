import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import HTTPException

from app.main import app
import app.api.v1.routes.image as image_routes


client = TestClient(app)


# ============================================================
# GLOBAL AUTH OVERRIDE (applies to ALL tests)
# ============================================================
@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[image_routes.get_current_user] = lambda: {
        "id": "user123",
        "email": "test@example.com",
        "role": "admin",
    }
    yield
    app.dependency_overrides.clear()


# ============================================================
# POST /image/image-upload
# ============================================================

@patch("app.api.v1.routes.image.upload_image_to_blob")
@patch("app.api.v1.routes.image.save_upload_record")
def test_image_upload_success(mock_save, mock_upload):
    mock_upload.return_value = "http://blob/image.png"

    res = client.post(
        "/image/image-upload",
        data={"category": "fsdu", "image_name": "img.png"},
        files={"file": ("img.png", b"data")}
    )

    assert res.status_code == 200
    assert res.json()["data"]["url"] == "http://blob/image.png"


def test_image_upload_missing_file():
    res = client.post(
        "/image/image-upload",
        data={"category": "fsdu", "image_name": "img.png"}
    )

    assert res.status_code == 422


@patch("app.api.v1.routes.image.upload_image_to_blob")
def test_image_upload_service_failure(mock_upload):
    mock_upload.side_effect = HTTPException(500, "Upload failed")

    res = client.post(
        "/image/image-upload",
        data={"category": "fsdu", "image_name": "img.png"},
        files={"file": ("img.png", b"data")}
    )

    assert res.status_code == 500


# ============================================================
# GET /image/gallery
# ============================================================

@patch("app.api.v1.routes.image.list_images")
def test_get_gallery_success(mock_list):
    mock_list.return_value = {"fsdu": []}

    res = client.get("/image/gallery?category=fsdu")

    assert res.status_code == 200
    assert "fsdu" in res.json()["data"]


@patch("app.api.v1.routes.image.list_images")
def test_get_gallery_invalid_category(mock_list):
    mock_list.side_effect = HTTPException(400, "Invalid category")

    res = client.get("/image/gallery?category=invalid")

    assert res.status_code == 400


# ============================================================
# GET /image/v1-template-gallery
# ============================================================

@patch("app.api.v1.routes.image.v1_list_images")
def test_template_gallery_success(mock_list):
    mock_list.return_value = {"items": [], "total": 0}

    res = client.get(
        "/image/v1-template-gallery?category=fsdu&page=1&page_size=10"
    )

    assert res.status_code == 200
    assert "data" in res.json()


def test_template_gallery_invalid_page():
    res = client.get(
        "/image/v1-template-gallery?category=fsdu&page=0&page_size=10"
    )

    assert res.status_code == 422


# ============================================================
# DELETE /image/delete-image
# ============================================================

@patch("app.api.v1.routes.image.delete_image_from_blob")
@patch("app.api.v1.routes.image.delete_upload_record")
def test_delete_image_success(mock_db, mock_blob):
    mock_blob.return_value = {"deleted": True}
    mock_db.return_value = {"id": "1"}

    res = client.delete(
        "/image/delete-image",
        params={"url": "http://blob/image.png"}
    )

    assert res.status_code == 200
    assert res.json()["data"]["blob_deleted"]["deleted"] is True


@patch("app.api.v1.routes.image.delete_image_from_blob")
def test_delete_image_blob_failure(mock_blob):
    mock_blob.side_effect = HTTPException(500, "Delete failed")

    res = client.delete(
        "/image/delete-image",
        params={"url": "http://blob/image.png"}
    )

    assert res.status_code == 500


# ============================================================
# POST /image/refinement-upload
# ============================================================

@patch("app.api.v1.routes.image.refinement_image_upload")
@patch("app.api.v1.routes.image.save_refinement_to_cosmos")
def test_refinement_upload_success(mock_save, mock_upload):
    mock_upload.return_value = "http://blob/refine.png"

    res = client.post(
        "/image/refinement-upload",
        data={
            "project_id": "p1",
            "stage": "Graphics",
            "image_name": "ref.png"
        },
        files={"file": ("ref.png", b"data")}
    )

    assert res.status_code == 200
    assert "url" in res.json()["data"]


def test_refinement_upload_missing_stage():
    res = client.post(
        "/image/refinement-upload",
        data={"project_id": "p1", "image_name": "ref.png"},
        files={"file": ("ref.png", b"data")}
    )

    assert res.status_code == 422


# ============================================================
# DELETE /image/refinement-delete
# ============================================================

@patch("app.api.v1.routes.image.delete_refinement")
def test_refinement_delete_success(mock_delete):
    mock_delete.return_value = {"deleted": True}

    res = client.delete(
        "/image/refinement-delete",
        params={"project_id": "p1", "url": "http://blob/ref.png"}
    )

    assert res.status_code == 200
    assert res.json()["data"]["deleted"] is True


@patch("app.api.v1.routes.image.delete_refinement")
def test_refinement_delete_failure(mock_delete):
    mock_delete.side_effect = HTTPException(404, "Not found")

    res = client.delete(
        "/image/refinement-delete",
        params={"project_id": "p1", "url": "http://blob/ref.png"}
    )

    assert res.status_code == 404


# ============================================================
# POST /image/image-exist
# ============================================================

@patch("app.api.v1.routes.image.image_exist_in_blob")
def test_image_exist_true(mock_exist):
    mock_exist.return_value = {"exists": True}

    res = client.post(
        "/image/image-exist",
        data={"category": "fsdu", "image_name": "img.png"}
    )

    assert res.status_code == 200
    assert res.json()["data"]["exists"] is True


def test_image_exist_missing_name():
    res = client.post(
        "/image/image-exist",
        data={"category": "fsdu"}
    )

    assert res.status_code == 422


# ============================================================
# POST /image/v1-image-upload
# ============================================================

@patch("app.api.v1.routes.image.upload_image_v1")
@patch("app.api.v1.routes.image.save_upload_record")
def test_v1_image_upload_success(mock_save, mock_upload):
    mock_upload.return_value = {
        "url": "http://blob/new.png",
        "image_name": "new.png"
    }

    res = client.post(
        "/image/v1-image-upload",
        data={
            "category": "fsdu",
            "image_name": "new.png",
            "action": "overwrite"
        },
        files={"file": ("new.png", b"data")}
    )

    assert res.status_code == 200
    assert res.json()["data"]["url"] == "http://blob/new.png"


def test_v1_image_upload_missing_action():
    res = client.post(
        "/image/v1-image-upload",
        data={"category": "fsdu", "image_name": "new.png"},
        files={"file": ("new.png", b"data")}
    )

    assert res.status_code == 422
