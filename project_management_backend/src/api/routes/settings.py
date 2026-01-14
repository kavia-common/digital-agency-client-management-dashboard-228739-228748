from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.schemas.settings import UserSettingsResponse, UserSettingsUpdateRequest
from src.auth.jwt import get_current_user
from src.db.models import User, UserSettings
from src.db.session import get_db

router = APIRouter(prefix="/settings", tags=["settings"])

_ALLOWED_THEMES = {"light", "dark"}


def _get_or_create_settings(db: Session, *, user_id: int) -> UserSettings:
    """Fetch settings row for user, creating it with defaults if missing."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if settings is None:
        settings = UserSettings(user_id=user_id, theme="light")
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get(
    "",
    response_model=UserSettingsResponse,
    summary="Get current user's settings",
    description="Retrieve persisted settings for the authenticated user (currently only theme).",
    operation_id="settings_get",
)
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSettingsResponse:
    """Get settings for the current authenticated user."""
    settings = _get_or_create_settings(db, user_id=current_user.id)
    return UserSettingsResponse(theme=settings.theme)


@router.put(
    "",
    response_model=UserSettingsResponse,
    summary="Update current user's settings",
    description="Update persisted settings for the authenticated user (currently only theme).",
    operation_id="settings_update",
)
def update_settings(
    payload: UserSettingsUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSettingsResponse:
    """Update settings for the current authenticated user."""
    theme = (payload.theme or "").strip().lower()
    if theme not in _ALLOWED_THEMES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid theme. Supported values: {', '.join(sorted(_ALLOWED_THEMES))}",
        )

    settings = _get_or_create_settings(db, user_id=current_user.id)
    settings.theme = theme
    db.commit()
    db.refresh(settings)
    return UserSettingsResponse(theme=settings.theme)
