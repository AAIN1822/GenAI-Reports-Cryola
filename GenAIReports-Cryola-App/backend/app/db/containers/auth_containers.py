from azure.cosmos.partition_key import PartitionKey
from app.db.db_config import (
    USER_CONTAINER,
    PASSWORD_RESET_CONTAINER,
    ACTIVITY_CONTAINER,
    ROLES_CONTAINER,
    USER_MASTER_LIST_CONTAINER,
)

def init_auth_containers(database):
    """Create authentication-related Cosmos DB containers"""

    user_masterlist = database.create_container_if_not_exists(
        id=USER_MASTER_LIST_CONTAINER,
        partition_key=PartitionKey(path="/email")
    )

    users = database.create_container_if_not_exists(
        id=USER_CONTAINER,
        partition_key=PartitionKey(path="/email")
    )

    otp = database.create_container_if_not_exists(
        id=PASSWORD_RESET_CONTAINER,
        partition_key=PartitionKey(path="/email")
    )

    activity = database.create_container_if_not_exists(
        id=ACTIVITY_CONTAINER,
        partition_key=PartitionKey(path="/user_id")
    )

    roles = database.create_container_if_not_exists(
        id=ROLES_CONTAINER,
        partition_key=PartitionKey(path="/role")
    )

    return {
        USER_MASTER_LIST_CONTAINER: user_masterlist,
        USER_CONTAINER: users,
        PASSWORD_RESET_CONTAINER: otp,
        ACTIVITY_CONTAINER: activity,
        ROLES_CONTAINER: roles,
    }
