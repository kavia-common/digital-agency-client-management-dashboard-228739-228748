from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RecentClientItem(BaseModel):
    """A small client projection for dashboard recents."""

    id: int = Field(..., description="Client id.")
    name: str = Field(..., description="Client name.")
    created_at: datetime = Field(..., description="Creation timestamp (UTC).")

    model_config = {"from_attributes": True}


class RecentProjectItem(BaseModel):
    """A small project projection for dashboard recents."""

    id: int = Field(..., description="Project id.")
    name: str = Field(..., description="Project name.")
    status: str = Field(..., description="Project status.")
    created_at: datetime = Field(..., description="Creation timestamp (UTC).")

    model_config = {"from_attributes": True}


class DashboardCounts(BaseModel):
    """High-level counts for the dashboard."""

    total_clients: int = Field(..., ge=0, description="Total number of clients owned by the current user.")
    total_projects: int = Field(..., ge=0, description="Total number of projects owned by the current user.")
    projects_by_status: Dict[str, int] = Field(
        default_factory=dict,
        description="Counts of projects grouped by status for the current user.",
    )


class DashboardAnalyticsResponse(BaseModel):
    """Dashboard analytics payload."""

    counts: DashboardCounts = Field(..., description="Aggregate counts for the dashboard.")
    recent_clients: List[RecentClientItem] = Field(
        default_factory=list,
        description="Most recently created clients (up to limit).",
    )
    recent_projects: List[RecentProjectItem] = Field(
        default_factory=list,
        description="Most recently created projects (up to limit).",
    )
