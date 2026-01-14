from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from src.auth.jwt import create_access_token, get_current_user
from src.auth.passwords import hash_password, verify_password
from src.db.models import User
from src.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user with a hashed password. Email must be unique.",
    operation_id="auth_register",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    """Register a new user.

    Args:
        payload: Email and plaintext password.
        db: SQLAlchemy session.

    Returns:
        The created user (without password).
    """
    existing = db.query(User).filter(User.email == str(payload.email)).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=str(payload.email), password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Verifies email/password and returns a JWT access token.",
    operation_id="auth_login",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Login a user and return a JWT.

    Args:
        payload: Email and plaintext password.
        db: SQLAlchemy session.

    Returns:
        JWT access token.
    """
    user = db.query(User).filter(User.email == str(payload.email)).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Returns the currently authenticated user inferred from the Bearer token.",
    operation_id="auth_me",
)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Get the current authenticated user."""
    return UserResponse.model_validate(current_user)
