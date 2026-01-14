from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.api.schemas.dashboard import (
    DashboardAnalyticsResponse,
    DashboardCounts,
    RecentClientItem,
    RecentProjectItem,
)
from src.auth.jwt import get_current_user
from src.db.models import Client, Project, User
from src.db.session import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "/analytics",
    response_model=DashboardAnalyticsResponse,
    summary="Get dashboard analytics",
    description=(
        "Returns aggregate counts and recent items for the authenticated user.\n\n"
        "Includes:\n"
        "- total_clients\n"
        "- total_projects\n"
        "- projects_by_status (grouped counts)\n"
        "- recent_clients (last N)\n"
        "- recent_projects (last N)"
    ),
    operation_id="dashboard_get_analytics",
)
def get_dashboard_analytics(
    recent_limit: int = Query(5, ge=1, le=25, description="Number of recent items to include per resource."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardAnalyticsResponse:
    """Get dashboard analytics for the currently authenticated user.

    Args:
        recent_limit: Number of recent clients/projects to return.
        db: SQLAlchemy session.
        current_user: Authenticated user (from JWT).

    Returns:
        Counts and recent items for the user's dashboard.
    """
    total_clients = (
        db.query(func.count(Client.id))
        .filter(Client.owner_id == current_user.id)
        .scalar()
        or 0
    )
    total_projects = (
        db.query(func.count(Project.id))
        .filter(Project.owner_id == current_user.id)
        .scalar()
        or 0
    )

    # Group project counts by status for the current user.
    status_rows = (
        db.query(Project.status, func.count(Project.id))
        .filter(Project.owner_id == current_user.id)
        .group_by(Project.status)
        .all()
    )
    projects_by_status: Dict[str, int] = {status: int(count) for status, count in status_rows}

    recent_clients_raw: List[Client] = (
        db.query(Client)
        .filter(Client.owner_id == current_user.id)
        .order_by(Client.created_at.desc())
        .limit(recent_limit)
        .all()
    )

    recent_projects_raw: List[Project] = (
        db.query(Project)
        .filter(Project.owner_id == current_user.id)
        .order_by(Project.created_at.desc())
        .limit(recent_limit)
        .all()
    )

    return DashboardAnalyticsResponse(
        counts=DashboardCounts(
            total_clients=int(total_clients),
            total_projects=int(total_projects),
            projects_by_status=projects_by_status,
        ),
        recent_clients=[RecentClientItem.model_validate(c) for c in recent_clients_raw],
        recent_projects=[RecentProjectItem.model_validate(p) for p in recent_projects_raw],
    )
