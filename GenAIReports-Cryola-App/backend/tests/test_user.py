import pytest, time
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from app.main import app
from app.core.security import get_current_user

client = TestClient(app)

# -------------------------------------------------------------------
# Mock Users
# -------------------------------------------------------------------

VALID_USER = {
    "id": "user123",
    "name": "Test User",
    "email": "test@example.com",
    "role_id": "admin",
    "login_type": "password",
    "last_login_time": int(time.time()),
    "hashed_password": "$2b$12$fakehash",
}

# -------------------------------------------------------------------
# Dependency Overrides
# -------------------------------------------------------------------

def override_get_current_user_valid():
    return VALID_USER

def override_get_current_user_none():
    return None

def override_get_current_user_unauthorized():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized"
    )

# -------------------------------------------------------------------
# /user/me Tests
# -------------------------------------------------------------------

def test_get_current_user_profile_success():
    app.dependency_overrides[get_current_user] = override_get_current_user_valid

    response = client.get("/user/me")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "User details fetched successfully"
    assert body["data"]["email"] == VALID_USER["email"]
    assert body["data"]["id"] == VALID_USER["id"]
    app.dependency_overrides.clear()


def test_get_current_user_profile_user_not_found():
    app.dependency_overrides[get_current_user] = override_get_current_user_none
    response = client.get("/user/me")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]
    app.dependency_overrides.clear()


def test_get_current_user_profile_unauthorized():
    app.dependency_overrides[get_current_user] = override_get_current_user_unauthorized
    response = client.get("/user/me")
    assert response.status_code == 401
    app.dependency_overrides.clear()


# -------------------------------------------------------------------
# /user/change-password Tests
# -------------------------------------------------------------------

def mock_handle_change_password_success(old, new, user):
    return True

def mock_handle_change_password_invalid_old(old, new, user):
    raise Exception("Invalid old password")

def mock_handle_change_password_internal_error(old, new, user):
    raise Exception("Database error")


def test_change_password_success(monkeypatch):
    app.dependency_overrides[get_current_user] = override_get_current_user_valid
    monkeypatch.setattr(
        "app.api.v1.routes.user.handle_change_password",
        mock_handle_change_password_success
    )
    response = client.post(
        "/user/change-password",
        json={
            "old_password": "Old@123",
            "new_password": "New@123"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"
    app.dependency_overrides.clear()


def test_change_password_invalid_old_password(monkeypatch):
    app.dependency_overrides[get_current_user] = override_get_current_user_valid
    monkeypatch.setattr(
        "app.api.v1.routes.user.handle_change_password",
        mock_handle_change_password_invalid_old
    )
    response = client.post(
        "/user/change-password",
        json={
            "old_password": "WrongOld",
            "new_password": "New@123"
        }
    )
    assert response.status_code == 500
    assert "Invalid old password" in response.json()["detail"]
    app.dependency_overrides.clear()


def test_change_password_internal_error(monkeypatch):
    app.dependency_overrides[get_current_user] = override_get_current_user_valid
    monkeypatch.setattr(
        "app.api.v1.routes.user.handle_change_password",
        mock_handle_change_password_internal_error
    )
    response = client.post(
        "/user/change-password",
        json={
            "old_password": "Old@123",
            "new_password": "New@123"
        }
    )
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]
    app.dependency_overrides.clear()


def test_change_password_unauthorized():
    app.dependency_overrides[get_current_user] = override_get_current_user_unauthorized
    response = client.post(
        "/user/change-password",
        json={
            "old_password": "Old@123",
            "new_password": "New@123"
        }
    )
    assert response.status_code == 401
    app.dependency_overrides.clear()
