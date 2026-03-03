from app.utils.datetime_helper import utc_unix
from app.db.db_config import (
    ACCOUNTS_CONTAINER,
    STRUCTURES_CONTAINER,
    SUBBRANDS_CONTAINER,
    REGIONS_CONTAINER,
    SEASONS_CONTAINER,
    DISPLAY_DIMENSIONS_CONTAINER,
    PRODUCT_DIMENSIONS_CONTAINER,
)
from app.db.session import get_db
from uuid import uuid4

ENTITY_NAMES = [
    ACCOUNTS_CONTAINER,
    STRUCTURES_CONTAINER,
    SUBBRANDS_CONTAINER,
    REGIONS_CONTAINER,
    SEASONS_CONTAINER,
    DISPLAY_DIMENSIONS_CONTAINER,
    PRODUCT_DIMENSIONS_CONTAINER,
]

MASTER_DATA_DEFAULTS = {
    ACCOUNTS_CONTAINER: [
        {"name": "Standard / All Accounts"},
        {"name": "Walmart"},
        {"name": "Target"},
        {"name": "Kroger"},
        {"name": "Fred Meyer"},
        {"name": "Meijer"},
        {"name": "Dollar General"},
        {"name": "Family Dollar"},
    ],
    STRUCTURES_CONTAINER: [
        {"name": "Inspirational"},
        {"name": "Bin"},
        {"name": "Clip Strip"},
        {"name": "Destination"},
        {"name": "Endcap"},
        {"name": "Floor Display"},
        {"name": "Pallet - Full"},
        {"name": "Pallet - Half"},
        {"name": "Pallet - Quarter"},
        {"name": "Plan-o-gram"},
        {"name": "Platform"},
        {"name": "Power Panel"},
        {"name": "Riser"},
        {"name": "Shelf"},
        {"name": "Signage"},
        {"name": "Standee"},
        {"name": "Train"},
        {"name": "Tray"},
    ],
    SUBBRANDS_CONTAINER: [
        {"name": "Clicks"},
        {"name": "Aged Up"},
        {"name": "Create Confidence"},
        {"name": "ACT"},
        {"name": "Art with Edge"},
        {"name": "B2C"},
        {"name": "Color and Erase"},
        {"name": "Color Equity"},
        {"name": "Color Wonder"},
        {"name": "Colors of Kindness"},
        {"name": "Colors of the World"},
        {"name": "Colourwhirls"},
        {"name": "Core"},
        {"name": "Creations"},
        {"name": "Creative Enthusiast"},
        {"name": "Glitter Dots"},
        {"name": "Globbles"},
        {"name": "Glo Fusion"},
        {"name": "Goo"},
        {"name": "Licensed Scribble Scrubbies"},
        {"name": "Light Play"},
        {"name": "Light - Up Tracing Pad"},
        {"name": "Little Hands Big Ideas"},
        {"name": "Mini Kids"},
        {"name": "Model Magic"},
        {"name": "Multicultural"},
        {"name": "My First"},
        {"name": "Paint & Peel Mosaic"},
        {"name": "Pops"},
        {"name": "Scribble Scrubbies / Colour & Wash / Washimals"},
        {"name": "Signature"},
        {"name": "Silly Putty"},
        {"name": "Silly Scents / Scented"},
        {"name": "STEAM"},
        {"name": "Swirl"},
        {"name": "Take Note"},
        {"name": "Toy"},
        {"name": "Young Kids"},
    ],

    REGIONS_CONTAINER: [
        {"name": "US"},
        {"name": "Canada"},
        {"name": "North America"},
        {"name": "Europe"},
    ],
    SEASONS_CONTAINER: [
        {"name": "Spring"},
        {"name": "Summer"},
        {"name": "Fall"},
        {"name": "Holiday"},
        {"name": "BTS"},
        {"name": "Halloween"},
        {"name": "Easter"},
        {"name": "Return to School"},
    ],
    DISPLAY_DIMENSIONS_CONTAINER: [
        {"name": "Height"},
        {"name": "Width"},
    ],
    PRODUCT_DIMENSIONS_CONTAINER: [
        {"name": "Height"},
        {"name": "Width"},
        {"name": "Depth"},
    ],
}


def seed_master_data():
    db = get_db()
    for entity_name in ENTITY_NAMES:
        container = db[entity_name]
        existing_count = list(
            container.query_items(
                query="SELECT VALUE COUNT(1) FROM c",
                enable_cross_partition_query=True,
            )
        )[0]

        if existing_count == 0:
            print(f"[SEEDING] Inserting defaults into: {entity_name}")
            default_items = MASTER_DATA_DEFAULTS.get(entity_name, [])
            for item in default_items:
                item["id"] = str(uuid4())
                item["active"] = True
                item["created_at"] = utc_unix()

                container.create_item(body=item)
        else:
            print(f"[SKIPPED] {entity_name} already contains data")