import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.core import security
from app.services import masterdata_service

from app.db.db_config import (
    ACCOUNTS_CONTAINER,
    STRUCTURES_CONTAINER,
    SUBBRANDS_CONTAINER,
    REGIONS_CONTAINER,
    SEASONS_CONTAINER,
    DISPLAY_DIMENSIONS_CONTAINER,
    PRODUCT_DIMENSIONS_CONTAINER,
    USER_MASTER_LIST_CONTAINER,
)

# ───────────────────────────────────────────────
# MOCK USER
# ───────────────────────────────────────────────

MOCK_USER = {
    "id": "user_123",
    "email": "test@example.com"
}

# ───────────────────────────────────────────────
# MOCK CONTAINER (NO COSMOS CALLS)
# ───────────────────────────────────────────────

class MockContainer:
    def __init__(self):
        self.items = {}

    def query_items(self, query, parameters=None, enable_cross_partition_query=True):
        if parameters:
            key = parameters[0]["value"]
            return [self.items[key]] if key in self.items else []
        return list(self.items.values())

    def create_item(self, body):
        body["id"] = body.get("id") or str(len(self.items) + 1)
        body.setdefault("created_by", MOCK_USER["id"])
        self.items[body["id"]] = body
        return body

    def read_item(self, item, partition_key):
        if item not in self.items:
            raise HTTPException(status_code=404)
        return self.items[item]

    def delete_item(self, item, partition_key):
        if item not in self.items:
            raise HTTPException(status_code=404)
        del self.items[item]

# ───────────────────────────────────────────────
# FIXTURES
# ───────────────────────────────────────────────

@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[security.get_current_user] = lambda: MOCK_USER
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def db(monkeypatch):
    containers = {
        ACCOUNTS_CONTAINER: MockContainer(),
        STRUCTURES_CONTAINER: MockContainer(),
        SUBBRANDS_CONTAINER: MockContainer(),
        REGIONS_CONTAINER: MockContainer(),
        SEASONS_CONTAINER: MockContainer(),
        DISPLAY_DIMENSIONS_CONTAINER: MockContainer(),
        PRODUCT_DIMENSIONS_CONTAINER: MockContainer(),
        USER_MASTER_LIST_CONTAINER: MockContainer(),
    }

    monkeypatch.setattr(
        "app.api.v1.routes.masterdata.get_db",
        lambda: containers
    )
    return containers


@pytest.fixture(autouse=True)
def mock_check_unique(monkeypatch):
    monkeypatch.setattr(
        "app.api.v1.routes.masterdata.check_unique",
        lambda container, name: True
    )

# TestClient MUST be created AFTER db fixture
@pytest.fixture
def client(db):
    return TestClient(app)

# ───────────────────────────────────────────────
# MASTER DATA – LIST
# ───────────────────────────────────────────────

def test_list_master_data_success(client):
    res = client.get(f"/master/{ACCOUNTS_CONTAINER}")
    assert res.status_code == 200
    assert res.json()["data"]["total"] == 0

# ───────────────────────────────────────────────
# MASTER DATA – CREATE
# ───────────────────────────────────────────────

def test_create_master_data_success(client):
    res = client.post(
        f"/master/{ACCOUNTS_CONTAINER}",
        json={"name": "Nike"}
    )
    assert res.status_code == 200


def test_create_master_data_duplicate(monkeypatch, client):
    monkeypatch.setattr(
        "app.api.v1.routes.masterdata.check_unique",
        lambda container, name: False
    )
    res = client.post(
        f"/master/{ACCOUNTS_CONTAINER}",
        json={"name": "Nike"}
    )
    assert res.status_code == 409

# ───────────────────────────────────────────────
# MASTER DATA – DELETE
# ───────────────────────────────────────────────

def test_delete_master_data_success(client, db):
    client.post(f"/master/{ACCOUNTS_CONTAINER}", json={"name": "Puma"})
    item_id = next(iter(db[ACCOUNTS_CONTAINER].items))
    res = client.delete(f"/master/{ACCOUNTS_CONTAINER}/{item_id}")
    assert res.status_code == 200


def test_delete_master_data_forbidden(client, db):
    db[ACCOUNTS_CONTAINER].items["1"] = {
        "id": "1",
        "name": "Adidas",
        "created_by": "another_user"
    }
    res = client.delete(f"/master/{ACCOUNTS_CONTAINER}/1")
    assert res.status_code == 403


def test_delete_master_data_not_found(client):
    res = client.delete(f"/master/{ACCOUNTS_CONTAINER}/999")
    assert res.status_code == 404

# ───────────────────────────────────────────────
# MD USER – LIST
# ───────────────────────────────────────────────

def test_list_md_users(client, db):
    db[USER_MASTER_LIST_CONTAINER].items["a@b.com"] = {
        "id": "a@b.com",
        "email": "a@b.com",
        "is_active": True
    }
    res = client.get("/master/list-user")
    assert res.status_code == 200
    assert res.json()["data"]["total"] == 1

# ───────────────────────────────────────────────
# MD USER – ADD
# ───────────────────────────────────────────────

def test_add_md_user_success(client):
    res = client.post(
        "/master/add-user",
        json={"email": "new@user.com", "is_active": True}
    )
    assert res.status_code == 200


def test_add_md_user_duplicate(client, db):
    db[USER_MASTER_LIST_CONTAINER].items["dup@user.com"] = {
        "id": "dup@user.com"
    }
    res = client.post(
        "/master/add-user",
        json={"email": "dup@user.com", "is_active": True}
    )
    assert res.status_code == 409

# ───────────────────────────────────────────────
# MD USER – DELETE
# ───────────────────────────────────────────────

def test_delete_md_user_success(client, db):
    db[USER_MASTER_LIST_CONTAINER].items["del@user.com"] = {
        "id": "del@user.com"
    }
    res = client.delete("/master/delete-user/del@user.com")
    assert res.status_code == 200


def test_delete_md_user_not_found(client):
    res = client.delete("/master/delete-user/no@user.com")
    assert res.status_code == 404
