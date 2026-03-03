"""
Authentication helper module for FastAPI.
Handles password hashing, JWT generation/verification,
and retrieving logged-in user using Cosmos DB Core API.
"""

from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi import HTTPException, status, Depends
from app.utils.datetime_helper import utc_now
from app.db.db_config import USER_CONTAINER
from passlib.context import CryptContext
from fastapi.security import HTTPBearer
from app.core.config import settings
from app.db.session import get_db
from datetime import timedelta
from jose import JWTError, jwt

security = HTTPBearer()

# JWT Config
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_HOURS = settings.JWT_REFRESH_TOKEN_EXPIRE_HOURS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ------------------------------------------
# Password utils
# ------------------------------------------
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# ------------------------------------------
# Token Creation
# ------------------------------------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = utc_now() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = utc_now() + (
        expires_delta or timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ------------------------------------------
# Verify Token
# ------------------------------------------
def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


# ------------------------------------------
# Get user from Cosmos DB Core API
# ------------------------------------------
def get_user(email: str):
    """
    Fetch user from Cosmos DB using email.
    """
    db = get_db()
    users_container = db[USER_CONTAINER]

    query = f"SELECT * FROM c WHERE c.email = '{email}'"
    results = list(
        users_container.query_items(
            query=query, enable_cross_partition_query=True
        )
    )
    return results[0] if results else None


# ------------------------------------------
# fetch current logged-in user
# ------------------------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=401,
                detail="Could not validate authentication credentials"
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token or expired session"
        )

    user = get_user(email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found or disabled"
        )
    return user