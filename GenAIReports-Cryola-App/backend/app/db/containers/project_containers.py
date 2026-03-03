from app.db.db_config import PROJECTS_CONTAINER, IMAGES_CONTAINER, FEEDBACK_CONTAINER, JOBS_CONTAINER
from azure.cosmos.partition_key import PartitionKey

def init_project_containers(database):
   
    projects = database.create_container_if_not_exists(
        id=PROJECTS_CONTAINER,
        partition_key=PartitionKey(path="/account")
    )

    images = database.create_container_if_not_exists(
        id=IMAGES_CONTAINER,
        partition_key=PartitionKey(path="/category")
    )

    feedback = database.create_container_if_not_exists(
        id = FEEDBACK_CONTAINER,
        partition_key=PartitionKey(path="/project_id")
    )

    jobs = database.create_container_if_not_exists(
        id = JOBS_CONTAINER,
        partition_key=PartitionKey(path="/id")
    )
    
    return {
        PROJECTS_CONTAINER: projects,
        IMAGES_CONTAINER: images,
        FEEDBACK_CONTAINER: feedback,
        JOBS_CONTAINER: jobs,
    }
