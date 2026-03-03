"""
Provides helper methods used by the password reset flow:
OTP generation, rate limiting per email, and expiration validation.
Cosmos DB Core API version.
"""

from app.db.db_config import PASSWORD_RESET_CONTAINER
from app.utils.datetime_helper import utc_now
from datetime import datetime, timedelta
from app.db.session import get_db
import random, string

# -------------------------------------------------------------------
# Configurable constants
# -------------------------------------------------------------------
OTP_LENGTH = 6
OTP_RATE_LIMIT_PER_HOUR = 5
OTP_EXPIRE_MINUTES = 5

def generate_otp(length: int = OTP_LENGTH) -> str:
    """Generate a numeric OTP of given length."""
    return "".join(random.choices(string.digits, k=length))


def check_otp_rate_limit(email: str) -> bool:
    """
    Check if OTP request count for email in past 1 hr <= OTP_RATE_LIMIT_PER_HOUR.
    Returns True if LIMIT NOT exceeded (allow OTP).
    Returns False if too many requests.
    """
    db = get_db()
    otp_container = db[PASSWORD_RESET_CONTAINER]
    one_hour_ago = (utc_now() - timedelta(hours=1)).isoformat()
    query = f"""
        SELECT VALUE COUNT(1)
        FROM c
        WHERE c.email = "{email}"
        AND c.created_at >= "{one_hour_ago}"
    """
    count = list(
        otp_container.query_items(
            query=query,
            enable_cross_partition_query=True
        )
    )[0]

    return count < OTP_RATE_LIMIT_PER_HOUR


def validate_otp(email: str, otp: str) -> bool:
    """Validate OTP and expiration."""
    db = get_db()
    otp_container = db[PASSWORD_RESET_CONTAINER]
    query = f"""
        SELECT * FROM c
        WHERE c.email = "{email}" AND c.otp = "{otp}"
    """

    items = list(
        otp_container.query_items(
            query=query,
            enable_cross_partition_query=True
        )
    )
    if not items:
        return False

    otp_data = items[0]
    expire_at = datetime.fromisoformat(
        otp_data["expire_at"].replace("Z", "+00:00")
    )
    return utc_now() <= expire_at