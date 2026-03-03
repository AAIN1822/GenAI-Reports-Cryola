from azure.cosmos.partition_key import PartitionKey
from app.db.db_config import (
    ACCOUNTS_CONTAINER,
    STRUCTURES_CONTAINER,
    SUBBRANDS_CONTAINER,
    REGIONS_CONTAINER,
    SEASONS_CONTAINER,
    DISPLAY_DIMENSIONS_CONTAINER,
    PRODUCT_DIMENSIONS_CONTAINER,
)

def init_master_containers(database):
    """Create master-data related Cosmos DB containers"""

    accounts = database.create_container_if_not_exists(
        id=ACCOUNTS_CONTAINER,
        partition_key=PartitionKey(path="/id")
    )

    structures = database.create_container_if_not_exists(
        id=STRUCTURES_CONTAINER,
        partition_key=PartitionKey(path="/id")
    )

    subbrands = database.create_container_if_not_exists(
        id=SUBBRANDS_CONTAINER,
        partition_key=PartitionKey(path="/id")
    )

    regions = database.create_container_if_not_exists(
        id=REGIONS_CONTAINER,
        partition_key=PartitionKey(path="/id")
    )

    seasons = database.create_container_if_not_exists(
        id=SEASONS_CONTAINER,
        partition_key=PartitionKey(path="/id")
    )

    display_dimensions = database.create_container_if_not_exists(
        id=DISPLAY_DIMENSIONS_CONTAINER,
        partition_key=PartitionKey(path="/id")
    )

    product_dimensions = database.create_container_if_not_exists(
        id=PRODUCT_DIMENSIONS_CONTAINER,
        partition_key=PartitionKey(path="/id")
    )

    return {
        ACCOUNTS_CONTAINER: accounts,
        STRUCTURES_CONTAINER: structures,
        SUBBRANDS_CONTAINER: subbrands,
        REGIONS_CONTAINER: regions,
        SEASONS_CONTAINER: seasons,
        DISPLAY_DIMENSIONS_CONTAINER: display_dimensions,
        PRODUCT_DIMENSIONS_CONTAINER: product_dimensions,
    }