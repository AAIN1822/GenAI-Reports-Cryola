from app.db.containers.project_containers import JOBS_CONTAINER
from app.utils.datetime_helper import utc_unix
from app.db.session import get_db
import ast

def create_job_status(job_id: str, project_id: str, stage: str, created_by: str):
    db = get_db()
    jobs_container = db[JOBS_CONTAINER]
    jobs_container.create_item({
        "id": job_id,
        "project_id": project_id,
        "stage": stage,
        "status": "IN_PROGRESS",
        "message": "Job started",
        "error": None,
        "started_at": utc_unix(),
        "created_by": created_by,
        "completed_at": None,
        "updated_at": utc_unix()
    })


def update_job_status(job_id: str, status: str, error: str = None, message: str = None):
    db = get_db()
    jobs_container = db[JOBS_CONTAINER]
    job = jobs_container.read_item(item=job_id, partition_key=job_id)
    job["status"] = status
    job["error"] = error
    job["message"] = message
    job["updated_at"] = utc_unix()
    if status in ("COMPLETED", "FAILED"):
        job["completed_at"] = utc_unix()

    jobs_container.replace_item(item=job_id, body=job)


# -------------------------------------------------------------------
def extract_error_message(exc: Exception) -> str:
    raw = str(exc)
    if "Error code:" in raw and "'error':" in raw and " - " in raw:
        try:
            json_part = raw.split(" - ", 1)[1].strip()
            data = ast.literal_eval(json_part)
            message = data.get("error", {}).get("message")
            code = data.get("error", {}).get("code")
            if code == "moderation_blocked" :
                return "This image appears to contain copyrighted or protected characters. For legal and safety reasons, we are unable to edit or generate images using this content. Please try again with an alternate image."
            return message.strip()
        except Exception:
            pass  # If parsing fails, return raw

    return raw
