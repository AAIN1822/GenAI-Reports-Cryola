"""
Authentication service module (Cosmos DB version).
Handles user registration and authentication using Azure Cosmos DB containers.
"""

from app.services.auth_helper import generate_otp, check_otp_rate_limit, OTP_EXPIRE_MINUTES
from app.db.db_config import USER_CONTAINER, ACTIVITY_CONTAINER, PASSWORD_RESET_CONTAINER
from app.schemas.user_schema import UserCreateSchema, UserLoginSchema, LoginResponse
from fastapi import HTTPException, status, BackgroundTasks
from app.schemas.user_register_schema import UserCreate
from app.schemas.activity_schema import ActivityLog
from app.services.email_service import send_reset_otp
from app.schemas.otp_schema import OtpSchema
from app.utils.datetime_helper import utc_now, utc_unix
from datetime import timedelta, datetime
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_HOURS,
)
from app.db.session import get_db
from uuid import uuid4

def register_user(user_data: UserCreateSchema):
    """
    Registers a new user in Cosmos DB.
    - Ensures email uniqueness
    - Hashes password before storing
    """

    db = get_db()
    user_container = db[USER_CONTAINER]

    # Check if user already exists
    existing = list(user_container.query_items(
        query="SELECT * FROM md_user u WHERE u.email = @email",
        parameters=[{"name": "@email", "value": user_data.email}],
        enable_cross_partition_query=False,
    ))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    new_user = UserCreate(
        id=str(uuid4()),
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role_id=user_data.role_id,
        status="active",
        login_type="local",
        created_time=utc_unix(),
        modified_time=utc_unix(),
        last_login_time=None,
    )
    user_container.create_item(body=new_user.model_dump())


def authenticate_user(login_data: UserLoginSchema) -> LoginResponse:
    """
    Authenticates user credentials.
    Generates JWT access & refresh tokens.
    Writes login activity entry in Cosmos DB.
    """

    db = get_db()
    user_container = db[USER_CONTAINER]
    activity_container = db[ACTIVITY_CONTAINER]

    # Get user by email (fast due to partition key)
    result = list(user_container.query_items(
        query="SELECT * FROM md_user u WHERE u.email = @email",
        parameters=[{"name": "@email", "value": login_data.email}],
        enable_cross_partition_query=False,
    ))

    if not result:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    user = result[0]
    if not verify_password(login_data.password, user.get("hashed_password")):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create tokens
    access_token = create_access_token(
        {"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        {"sub": user["email"]},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_HOURS),
    )

    # Update last_login_time
    user["last_login_time"] = utc_unix()
    user_container.upsert_item(body=user)

    # Insert activity log
    activity_log = ActivityLog(
        id=str(uuid4()),
        user_id=user["id"],
        login_time=utc_unix(),
        logout_time=None,
    )
    activity_container.create_item(body=activity_log.model_dump())

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES
    )

def handle_forgot_password(email: str, background_tasks: BackgroundTasks):
    db = get_db()
    user_container = db[USER_CONTAINER]
    otp_container = db[PASSWORD_RESET_CONTAINER]

    # Check if user exists
    user_result = list(user_container.query_items(
        query="SELECT * FROM md_user u WHERE u.email = @email",
        parameters=[{"name": "@email", "value": email}],
        enable_cross_partition_query=False
    ))
    if not user_result:
        raise HTTPException(status_code=404, detail="No account found with this email")

    if not check_otp_rate_limit(email):
        raise HTTPException(status_code=429, detail="Too many OTP requests. Try again later.")

    otp = generate_otp()
    expires_at = utc_now() + timedelta(minutes=OTP_EXPIRE_MINUTES)

    query = "SELECT c.id FROM c WHERE c.email = @email"
    params = [{"name": "@email", "value": email}]

    old_otps = list(otp_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    for otp_doc in old_otps:
        otp_container.delete_item(item=otp_doc["id"], partition_key=email)

    # Insert new OTP
    otp_data = OtpSchema(
        id=str(uuid4()),
        email=email,
        otp=otp,
        used=False,
        expires_at=expires_at.isoformat(),
        created_at=utc_unix()
    )
    otp_container.create_item(body=otp_data.model_dump())
    background_tasks.add_task(send_reset_otp, email, otp)


def handle_validate_otp(email: str, otp: str) -> str:
    db = get_db()
    otp_container = db[PASSWORD_RESET_CONTAINER]
    records = list(otp_container.query_items(
        query="SELECT * FROM md_password_reset_otp p WHERE p.email = @email AND p.otp = @otp",
        parameters=[{"name": "@email", "value": email}, {"name": "@otp", "value": otp}],
        enable_cross_partition_query=False,
    ))

    if not records:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    record = records[0]
    if record["used"]:
        raise HTTPException(status_code=400, detail="OTP already used")

    if datetime.fromisoformat(record["expires_at"]) < utc_now():
        raise HTTPException(status_code=400, detail="OTP expired")

    record["used"] = True
    otp_container.upsert_item(record)
    reset_token = create_access_token(
        {"sub": email, "type": "password_reset"},
        expires_delta=timedelta(minutes=5)
    )
    return reset_token


def handle_resend_otp(email: str, background_tasks: BackgroundTasks):
    db = get_db()
    user_container = db[USER_CONTAINER]
    otp_container = db[PASSWORD_RESET_CONTAINER]

    # Check if user exists
    user_result = list(user_container.query_items(
        query="SELECT * FROM md_user u WHERE u.email = @email",
        parameters=[{"name": "@email", "value": email}],
        enable_cross_partition_query=False
    ))

    if not user_result:
        raise HTTPException(status_code=404, detail="No account found with this email")

    # Rate limit check
    if not check_otp_rate_limit(email):
        raise HTTPException(status_code=429, detail="Too many OTP requests. Try again later.")

    otp = generate_otp()
    expires_at = utc_now() + timedelta(minutes=OTP_EXPIRE_MINUTES)

    # Remove old unused OTPs
    old_otps = list(otp_container.query_items(
        query="SELECT c.id FROM c WHERE c.email = @email",
        parameters=[{"name": "@email", "value": email}],
        enable_cross_partition_query=True
    ))
    for otp_doc in old_otps:
        otp_container.delete_item(item=otp_doc["id"], partition_key=email)

    # Insert new OTP
    otp_data = OtpSchema(
        id=str(uuid4()),
        email=email,
        otp=otp,
        used=False,
        expires_at=expires_at.isoformat(),
        created_at=utc_unix()
    )
    otp_container.create_item(body=otp_data.model_dump())

    # Send OTP email in background
    background_tasks.add_task(send_reset_otp, email, otp)


def handle_reset_password(new_password: str, password_reset_token: str):
    try:
        payload = verify_token(password_reset_token)
    except:
        raise HTTPException(status_code=403, detail="Invalid or expired password reset token")

    if payload.get("type") != "password_reset":
        raise HTTPException(status_code=403, detail="Invalid token type")

    email = payload.get("sub")

    db = get_db()
    user_container = db[USER_CONTAINER]

    results = list(user_container.query_items(
        query="SELECT * FROM md_user u WHERE u.email = @email",
        parameters=[{"name": "@email", "value": email}],
        enable_cross_partition_query=False,
    ))

    if not results:
        raise HTTPException(status_code=404, detail="User not found")

    user = results[0]
    user["hashed_password"] = hash_password(new_password)
    user_container.upsert_item(user)


def handle_logout(current_user: dict):
    db = get_db()
    activity_container = db[ACTIVITY_CONTAINER]
    # Write latest logout timestamp
    log = ActivityLog(
        id=str(uuid4()),
        user_id=current_user["id"],
        logout_time=utc_unix()
    )
    activity_container.create_item(body=log.model_dump())


def handle_refresh_token(refresh_token: str) -> str:
    # Decode / verify refresh token
    payload = verify_token(refresh_token)
    # Ensure token type is "refresh"
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Generate new access token
    new_access_token = create_access_token({"sub": payload.get("sub")})
    return new_access_token