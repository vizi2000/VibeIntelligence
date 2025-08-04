"""
Authentication API Routes
Following Directive 7: Security First
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
import jwt
from datetime import datetime, timedelta
import bcrypt

from ..core.config import settings
from ..core.exceptions import AuthenticationException

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization: Optional[str] = None
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    
class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    organization: Optional[str]
    vibe_score: int = 100
    eco_credits: int = 0
    created_at: datetime


# Temporary user storage (replace with database)
USERS_DB = {}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token with vibe-aware expiration"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Shorter tokens are more eco-friendly!
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "vibe": "high"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password with bcrypt"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def hash_password(password: str) -> str:
    """Hash password with bcrypt and good vibes"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        email: str = payload.get("sub")
        if email is None:
            raise AuthenticationException("Invalid token payload")
            
        # Get user from DB (mock for now)
        user = USERS_DB.get(email)
        if user is None:
            raise AuthenticationException("User not found")
            
        return user
        
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("Token has expired - time for a refresh! 🔄")
    except jwt.JWTError:
        raise AuthenticationException("Invalid token - let's get you a new one! 🔑")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user with vibecoding welcome
    Awards initial eco-credits for joining the movement
    """
    # Check if user exists
    if user_data.email in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered - welcome back! 👋"
        )
    
    # Create user with hashed password
    hashed_pwd = hash_password(user_data.password)
    
    user = {
        "id": f"user_{len(USERS_DB) + 1}",
        "email": user_data.email,
        "password": hashed_pwd,  # Store hashed
        "full_name": user_data.full_name,
        "organization": user_data.organization,
        "vibe_score": 100,  # Everyone starts with max vibes!
        "eco_credits": 50,  # Welcome bonus
        "created_at": datetime.utcnow()
    }
    
    USERS_DB[user_data.email] = user
    
    # Return user without password
    return UserResponse(**{k: v for k, v in user.items() if k != "password"})


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with email/password and receive JWT token
    Each login increases your vibe score!
    """
    # Get user
    user = USERS_DB.get(form_data.username)  # username is email
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password - no worries, try again! 🔐",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update vibe score for engagement
    user["vibe_score"] = min(100, user["vibe_score"] + 1)
    
    # Create token
    access_token = create_access_token(
        data={"sub": user["email"], "name": user["full_name"]}
    )
    
    return Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information with vibe status
    """
    # Remove password from response
    user_data = {k: v for k, v in current_user.items() if k != "password"}
    return UserResponse(**user_data)


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Refresh access token for continued vibing
    Eco-friendly: extends session without re-authentication
    """
    # Create new token
    access_token = create_access_token(
        data={"sub": current_user["email"], "name": current_user["full_name"]}
    )
    
    # Award eco credits for session extension
    current_user["eco_credits"] += 1
    
    return Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout endpoint (client-side token removal)
    Thanks for vibing with us! 🌟
    """
    # In JWT, logout is handled client-side
    # We can log the event for analytics
    return {
        "message": "Logged out successfully! See you soon 👋",
        "vibe_bonus": "Thanks for the great session!",
        "eco_credits_earned": 5
    }


@router.put("/vibe-boost")
async def boost_vibe(current_user: dict = Depends(get_current_user)):
    """
    Boost your vibe score (v4.0 feature)
    Daily vibe boost for mental wellness
    """
    # Check last boost time (mock implementation)
    current_vibe = current_user.get("vibe_score", 50)
    
    if current_vibe >= 100:
        return {
            "message": "Your vibe is already at maximum! 🌟",
            "vibe_score": 100,
            "tip": "Share the good vibes with others!"
        }
    
    # Boost vibe
    new_vibe = min(100, current_vibe + 10)
    current_user["vibe_score"] = new_vibe
    
    return {
        "message": "Vibe boosted! ✨",
        "vibe_score": new_vibe,
        "affirmation": "You're doing great! Keep up the positive energy!"
    }