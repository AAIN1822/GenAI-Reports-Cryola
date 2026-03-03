from app.db.containers.masterdata_containers import init_master_containers
from app.db.containers.project_containers import init_project_containers
from app.db.containers.auth_containers import init_auth_containers
from app.db.db_config import COSMOS_DB_NAME
from azure.cosmos import CosmosClient
from app.core.config import settings

_client = None
_database = None
_containers = None

def get_db():
    global _client, _database, _containers
    if _containers is None:
        _client = CosmosClient(
            settings.COSMOS_ENDPOINT,
            settings.COSMOS_KEY
        )
        _database = _client.create_database_if_not_exists(
            id=COSMOS_DB_NAME
        )
        _containers = {}
        _containers.update(init_auth_containers(_database))
        _containers.update(init_master_containers(_database))
        _containers.update(init_project_containers(_database))

    return _containers
