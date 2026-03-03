from app.utils.datetime_helper import utc_unix
from uuid import uuid4

def check_unique(container, name: str) -> bool:
    """
    Checks if an item with the given name already exists in the container.
    Returns True if the name is unique (not found), otherwise False.
    """
    query = "SELECT * FROM c WHERE LOWER(c.name) = @name"
    parameters = [{"name": "@name", "value": name.lower()}]
    existing_items = list(
        container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        )
    )
    return len(existing_items) == 0


def create_item(container, payload: dict) -> dict:
    """
    Creates a new item in the container with UUID and created_at timestamp.
    """
    item = payload.copy()
    item["id"] = str(uuid4())
    item["created_at"] = utc_unix()
    container.create_item(body=item)
    return item