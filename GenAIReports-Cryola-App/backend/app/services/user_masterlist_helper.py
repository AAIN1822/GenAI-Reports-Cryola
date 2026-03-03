from azure.cosmos.exceptions import CosmosResourceNotFoundError
from app.db.db_config import USER_MASTER_LIST_CONTAINER
from app.utils.datetime_helper import utc_unix
from app.db.session import get_db
from uuid import uuid4

MASTER_DATA_DEFAULTS = {
    USER_MASTER_LIST_CONTAINER: [
        {"email": "pss263@hallmark.com", "name": "vetrivel sivakumar"},
        {"email": "tgs925@hallmark.com", "name": "mathan mohan"},
        {"email": "snv677@hallmark.com", "name": "raja chellappan"},
        {"email": "xfr755@hallmark.com", "name": "balu nair"},
    ],
}

def seed_user_masterlist():
    db = get_db()
    container = db[USER_MASTER_LIST_CONTAINER]

    for item in MASTER_DATA_DEFAULTS[USER_MASTER_LIST_CONTAINER]:
        email = item["email"]
        name = item.get("name")

        query = "SELECT VALUE COUNT(1) FROM c WHERE c.email = @email"
        params = [{"name": "@email", "value": email}]

        count = list(container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))[0]

        if count == 0:
            doc = {
                "id": str(uuid4()),
                "email": email,
                "name": name,
                "is_active": True,
                "created_at": utc_unix(),
            }
            container.create_item(body=doc)
            print(f"[INSERTED] {email}")
