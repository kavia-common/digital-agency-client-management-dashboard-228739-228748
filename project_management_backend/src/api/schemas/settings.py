from __future__ import annotations

from pydantic import BaseModel, Field


class UserSettingsResponse(BaseModel):
    """User settings response model."""

    theme: str = Field(..., description="Theme preference. Supported values: light, dark.")


class UserSettingsUpdateRequest(BaseModel):
    """Payload to update user settings."""

    theme: str = Field(..., description="Theme preference. Supported values: light, dark.")
