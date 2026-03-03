import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from uuid import uuid4

from app.main import app
from app.services.sso_service import handle_sso_login
from app.schemas.user_register_schema import UserCreate
from app.db.db_config import USER_CONTAINER, ACTIVITY_CONTAINER

client = TestClient(app)

# =========================================================
# FIXTURES
# =========================================================

@pytest.fixture
def fake_payload():
    return {
        "preferred_username": "testuser@example.com",
        "name": "Test User"
    }


@pytest.fixture
def mock_db():
    user_container = MagicMock()
    activity_container = MagicMock()
    return {
        USER_CONTAINER: user_container,
        ACTIVITY_CONTAINER: activity_container
    }


# =========================================================
# SERVICE TESTS — handle_sso_login
# =========================================================

@patch("app.services.sso_service.validate_user_from_masterlist")
@patch("app.services.sso_service.verify_ms_id_token")
@patch("app.services.sso_service.get_db")
def test_sso_login_creates_new_user(
    mock_get_db,
    mock_verify,
    mock_validate,
    fake_payload,
    mock_db
):
    mock_verify.return_value = fake_payload
    mock_validate.return_value = None
    mock_get_db.return_value = mock_db

    mock_db[USER_CONTAINER].query_items.return_value = []

    access, refresh = handle_sso_login("fake_token", "admin")

    assert isinstance(access, str)
    assert isinstance(refresh, str)
    assert mock_db[USER_CONTAINER].upsert_item.call_count == 1
    assert mock_db[ACTIVITY_CONTAINER].create_item.call_count == 1


@patch("app.services.sso_service.validate_user_from_masterlist")
@patch("app.services.sso_service.verify_ms_id_token")
@patch("app.services.sso_service.get_db")
def test_sso_login_existing_user(
    mock_get_db,
    mock_verify,
    mock_validate,
    fake_payload,
    mock_db
):
    mock_verify.return_value = fake_payload
    mock_validate.return_value = None
    mock_get_db.return_value = mock_db

    existing_user = UserCreate(
        id=str(uuid4()),
        name="Existing User",
        email="testuser@example.com",
        role_id="admin",
        status="ACTIVE",
        login_type="SSO",
        created_time=123,
        modified_time=123,
        last_login_time=123,
    ).model_dump()

    mock_db[USER_CONTAINER].query_items.return_value = [existing_user]

    access, refresh = handle_sso_login("fake_token", "admin")

    assert isinstance(access, str)
    assert isinstance(refresh, str)
    assert mock_db[USER_CONTAINER].upsert_item.call_count == 1
    assert mock_db[ACTIVITY_CONTAINER].create_item.call_count == 1


@patch("app.services.sso_service.verify_ms_id_token")
def test_sso_login_missing_email(mock_verify):
    mock_verify.return_value = {"name": "Test User"}

    with pytest.raises(Exception) as exc:
        handle_sso_login("fake_token", "admin")

    assert "Email not present" in str(exc.value)


@patch("app.services.sso_service.verify_ms_id_token")
def test_sso_login_invalid_token(mock_verify):
    mock_verify.side_effect = HTTPException(
        status_code=401,
        detail="Invalid ID token"
    )

    with pytest.raises(HTTPException) as exc:
        handle_sso_login("bad_token", "admin")

    assert exc.value.status_code == 401


@patch("app.services.sso_service.validate_user_from_masterlist")
@patch("app.services.sso_service.verify_ms_id_token")
def test_sso_masterlist_rejected(mock_verify, mock_validate):
    mock_verify.return_value = {
        "preferred_username": "blocked@example.com"
    }
    mock_validate.side_effect = HTTPException(403, "Not allowed")

    with pytest.raises(HTTPException) as exc:
        handle_sso_login("fake_token", "admin")

    assert exc.value.status_code == 403


@patch("app.services.sso_service.verify_ms_id_token")
@patch("app.services.sso_service.get_db")
def test_sso_activity_log_failure(
    mock_get_db,
    mock_verify,
    fake_payload,
    mock_db
):
    mock_verify.return_value = fake_payload
    mock_get_db.return_value = mock_db
    mock_db[ACTIVITY_CONTAINER].create_item.side_effect = Exception("DB down")

    with pytest.raises(Exception):
        handle_sso_login("fake_token", "admin")


# =========================================================
# ROUTE TESTS — /auth/sso/login
# =========================================================

@patch("app.api.v1.routes.sso.handle_sso_login")
def test_sso_login_route_success(mock_handle):
    mock_handle.return_value = ("access123", "refresh123")

    res = client.post(
        "/auth/sso/login",
        json={
            "id_token": "fake_token",
            "role_id": "admin"
        }
    )

    assert res.status_code == 200
    data = res.json()["data"]

    assert data["access_token"] == "access123"
    assert data["refresh_token"] == "refresh123"
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


def test_sso_login_route_validation_error():
    res = client.post(
        "/auth/sso/login",
        json={"id_token": "fake_token"}
    )

    assert res.status_code == 422


@patch("app.api.v1.routes.sso.handle_sso_login")
def test_sso_login_route_http_exception(mock_handle):
    mock_handle.side_effect = HTTPException(
        status_code=401,
        detail="Unauthorized"
    )

    res = client.post(
        "/auth/sso/login",
        json={
            "id_token": "bad_token",
            "role_id": "admin"
        }
    )

    assert res.status_code == 401
    assert "Unauthorized" in res.json()["detail"]


@patch("app.api.v1.routes.sso.handle_sso_login")
def test_sso_login_route_internal_error(mock_handle):
    mock_handle.side_effect = Exception("Boom")

    res = client.post(
        "/auth/sso/login",
        json={
            "id_token": "fake_token",
            "role_id": "admin"
        }
    )

    assert res.status_code == 500
    assert "Internal server error" in res.json()["detail"]
