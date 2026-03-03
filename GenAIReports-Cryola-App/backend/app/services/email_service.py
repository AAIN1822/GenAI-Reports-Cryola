"""
Email utility module for sending password reset OTP emails using FastAPI-Mail.
Loads SMTP config from environment variables and sends formatted HTML OTP messages.
"""

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

# ---- Email configuration ----
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

# ---- Actual email sending ----
async def send_reset_otp(email: str, otp: str):
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
      <h3 style="color:#2b6cb0;">Password Reset OTP</h3>
      <p>Your OTP for password reset is: <strong>{otp}</strong></p>
      <p>This code is valid for <b>5 minutes</b>.</p>
      <p>If you didn’t request this, please ignore this email.</p>
    </body>
    </html>
    """
    message = MessageSchema(
        subject="Your Password Reset OTP",
        recipients=[email],
        body=body,
        subtype="html"
    )
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        logger.info(f"OTP email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")