from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address (unique).")
    password: str = Field(..., min_length=8, description="Plaintext password (min 8 characters).")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address.")
    password: str = Field(..., description="Plaintext password.")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token to use as 'Authorization: Bearer <token>'.")
    token_type: str = Field("bearer", description="Token type.")


class UserResponse(BaseModel):
    id: int = Field(..., description="User id.")
    email: EmailStr = Field(..., description="User email address.")

    model_config = {"from_attributes": True}
