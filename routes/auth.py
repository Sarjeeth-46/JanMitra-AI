"""
Authentication Routes

Provides login, register, application-status, and OTP endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from middleware.auth import create_access_token, verify_token
from datetime import timedelta
import logging
import time
from database.user_repository import UserRepository
from database.application_repository import ApplicationRepository
from database.otp_repository import OTPSessionRepository
from services.sns_service import SNSService
from passlib.context import CryptContext

router = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
user_repo = UserRepository()
app_repo = ApplicationRepository()
otp_repo = OTPSessionRepository()
sns_service = SNSService()

# ─── Request/Response models ──────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    language: Optional[str] = 'en'

class LoginRequest(BaseModel):
    email: str
    password: str

class SendOTPRequest(BaseModel):
    mobile: str

class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: str
    name: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class ApplicationStatusResponse(BaseModel):
    application_id: str
    status: str
    submitted_date: str
    estimated_approval: str
    scheme_name: str

# ─── Debug Fallback ───────────────────────────────────────────────────────────
@router.get("/auth/last-otp")
async def get_last_otp():
    """Fallback endpoint to see the last generated OTP if terminal is hidden."""
    try:
        import os
        if os.path.exists("otp_debug.txt"):
            with open("otp_debug.txt", "r") as f:
                return {"otp": f.read().strip()}
        return {"error": "No OTP generated yet"}
    except Exception as e:
        return {"error": str(e)}

# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/auth/send-otp")
async def send_otp(body: SendOTPRequest):
    """
    Validates mobile number and sends a 6-digit OTP.
    For Hackathon Demo Mode: Prints OTP to console.
    """
    mobile = body.mobile.strip()
    if not mobile.isdigit() or len(mobile) < 10:
        raise HTTPException(status_code=400, detail="Invalid Indian mobile number")
    
    import random
    otp = str(random.randint(100000, 999999))
    
    # Store in DynamoDB
    await otp_repo.save_otp(mobile, otp)
    
    # Real SMS Delivery via AWS SNS
    sms_message = f"<#>> JanMitra AI: Your verification code is {otp}. Valid for 5 mins."
    sns_service.send_sms(mobile, sms_message)

    # Demo Mode Print & File Fallback
    print(f"\n[OTP DEBUG] Mobile: {mobile} | Code: {otp}\n")
    
    try:
        with open("otp_debug.txt", "w") as f:
            f.write(otp)
    except:
        pass

    import sys
    sys.stdout.flush()
    
    logger.info(f"OTP_EVENT: Sent {otp} to {mobile}")
    return {"success": True, "message": "OTP sent successfully"}


@router.post("/auth/verify-otp", response_model=AuthResponse)
async def verify_otp(body: VerifyOTPRequest):
    """
    Verifies OTP and authenticates user. Creates user if not exists.
    """
    mobile = body.mobile.strip()
    otp = body.otp.strip()
    
    # Master OTP Bypass for Hackathon Demo
    if otp == "123456":
        logger.warning(f"MASTER_OTP used for {mobile}")
        is_valid = True
    else:
        is_valid = await otp_repo.verify_otp(mobile, otp)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")
    
    # Get or create user
    user = await user_repo.get_user_by_phone(mobile)
    if not user:
        user_name = body.name or f"User {mobile[-4:]}"
        user_data = {
            "name": user_name,
            "email": f"{mobile}@janmitra.ai",
            "phone": mobile,
            "created_at": str(time.time()),
            "language": "en"
        }
        await user_repo.create_user(user_data)
        user = user_data
    
    # Generate JWT
    email = user.get("email") or f"{mobile}@janmitra.ai"
    token = create_access_token(
        data={"sub": email, "name": user.get("name"), "phone": mobile},
        expires_delta=timedelta(hours=24)
    )
    
    logger.info(f"User {mobile} authenticated via OTP", extra={"event": "otp_login_success", "mobile": mobile})
    
    return AuthResponse(
        access_token=token,
        user={k: v for k, v in user.items() if k != "password_hash"}
    )


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(request: Request, body: RegisterRequest):
    """Register a new user account in DynamoDB."""
    email = body.email.lower().strip()
    
    # Check if user exists
    existing_user = await user_repo.get_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists."
        )
    
    # Hash password
    hashed_password = pwd_context.hash(body.password)
    
    user_data = {
        "name": body.name,
        "email": email,
        "phone": body.phone,
        "password_hash": hashed_password,
        "language": body.language or 'en'
    }
    
    await user_repo.create_user(user_data)
    
    logger.info("New user registered", extra={"event": "user_registered", "email": email})
    return {"message": "Account created successfully. Please log in."}


@router.post("/auth/login", response_model=AuthResponse)
async def login(request: Request, body: LoginRequest):
    """Authenticate a user using DynamoDB and return a JWT token."""
    email = body.email.lower().strip()
    user = await user_repo.get_user_by_email(email)
    
    if not user or not pwd_context.verify(body.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    token = create_access_token(
        data={"sub": email, "name": user["name"]},
        expires_delta=timedelta(hours=24)
    )
    
    logger.info("User login successful", extra={"event": "user_login", "email": email})
    
    # Return user profile without the password hash
    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    
    return AuthResponse(
        access_token=token,
        user=safe_user
    )


@router.get("/user/profile")
async def get_profile(token: dict = Depends(verify_token)):
    """Retrieve the current user's profile. Returns a Guest profile for anonymous tokens."""
    email = token.get("sub", "")

    # Anonymous or missing sub → return guest profile (never crash)
    if not email or email in ("anonymous_user", "anonymous"):
        return {"name": "Guest User", "email": "", "is_guest": True, "language": "en"}

    user = await user_repo.get_user_by_email(email)
    if not user:
        # Fallback to phone lookup if email not found (for OTP users)
        # Assuming email was stored as mobile@janmitra.ai
        user = await user_repo.get_user_by_phone(email.split('@')[0])
        if not user:
            return {"name": "Guest User", "email": email, "is_guest": True, "language": "en"}

    # Remove sensitive data
    return {k: v for k, v in user.items() if k != "password_hash"}


@router.get("/user/applications")
async def get_user_applications(token: dict = Depends(verify_token)):
    """Retrieve all applications for the current user. Returns [] for anonymous users."""
    email = token.get("sub", "")
    if not email or email in ("anonymous_user", "anonymous"):
        return []   # guest users have no applications
    apps = await app_repo.get_applications_by_user(email)
    return apps


@router.get("/application-status", response_model=ApplicationStatusResponse)
async def get_application_status(id: str, phone: str):
    """
    Look up application status by Application ID and Phone from DynamoDB.
    """
    if not id or not phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both Application ID and Phone number are required."
        )
    
    app = await app_repo.get_application_by_id_and_phone(id, phone)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found with provided ID and phone number."
        )
    
    return ApplicationStatusResponse(
        application_id=app['application_id'],
        status=app['status'],
        submitted_date=app['submitted_date'],
        estimated_approval=app['estimated_approval'],
        scheme_name=app['scheme_name']
    )
