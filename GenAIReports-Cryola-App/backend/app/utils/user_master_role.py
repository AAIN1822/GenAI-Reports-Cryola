"""
Seeds default user roles into Cosmos DB on application startup
(creates Admin and Designer roles if they don't already exist).
"""

from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError
from app.schemas.role_schema import RoleSchema
from app.utils.datetime_helper import utc_unix
from app.db.db_config import ROLES_CONTAINER
from app.db.session import get_db

def user_roles():
    print("Running user_roles seeding...")
    db = get_db()          
    roles_container = db[ROLES_CONTAINER]  
    default_roles = ["Admin", "Designer"]

    try:
        for role_name in default_roles:
            try:
                roles_container.read_item(item=role_name, partition_key=role_name)

            except CosmosResourceNotFoundError:
                # If not found, insert new record/document
                role = RoleSchema(
                    id=role_name,
                    role=role_name,
                    created_time=utc_unix(),
                    modified_time=utc_unix(),
                )

                roles_container.create_item(body=role.model_dump())

        print("Default roles verified/inserted successfully.")

    except CosmosHttpResponseError as e:
        print("Role seeding failed:", e)