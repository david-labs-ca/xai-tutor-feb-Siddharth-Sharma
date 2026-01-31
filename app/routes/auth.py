"""
Authentication routes: register and login with JWT.
"""

from fastapi import APIRouter, HTTPException, status

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest):
    """
    Register a new user. Email must be unique.
    Password is stored hashed.
    """
    if len(body.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters",
        )
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (body.email.lower(),))
        if cursor.fetchone() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        hashed = hash_password(body.password)
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (body.email.lower(), hashed),
        )
        user_id = cursor.lastrowid
    return {"id": user_id, "email": body.email.lower()}


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    """
    Login with email and password. Returns a JWT access token.
    Use the token in the Authorization header: Bearer <token>
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, password FROM users WHERE email = ?",
            (body.email.lower(),),
        )
        row = cursor.fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    user_id, email, hashed = row["id"], row["email"], row["password"]
    if not verify_password(body.password, hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token = create_access_token(data={"sub": str(user_id)})
    return {"access_token": access_token, "token_type": "bearer"}
