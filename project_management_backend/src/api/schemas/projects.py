from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


_ALLOWED_STATUSES = {"planned", "in_progress", "blocked", "completed", "cancelled"}


class ProjectBase(BaseModel):
    """Shared fields for project create/update payloads."""

    name: str = Field(..., min_length=1, max_length=200, description="Project name.")
    description: Optional[str] = Field(None, max_length=10000, description="Optional project description.")
    status: str = Field(
        "planned",
        description="Project status.",
        examples=["planned", "in_progress", "blocked", "completed", "cancelled"],
    )
    client_id: Optional[int] = Field(None, description="Optional associated client id.")
    start_date: Optional[date] = Field(None, description="Optional start date.")
    due_date: Optional[date] = Field(None, description="Optional due date.")


class ProjectCreate(ProjectBase):
    """Payload to create a project."""


class ProjectUpdate(BaseModel):
    """Payload to update a project (partial update semantics)."""

    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Project name.")
    description: Optional[str] = Field(None, max_length=10000, description="Optional project description.")
    status: Optional[str] = Field(
        None,
        description="Project status.",
        examples=["planned", "in_progress", "blocked", "completed", "cancelled"],
    )
    client_id: Optional[int] = Field(None, description="Optional associated client id.")
    start_date: Optional[date] = Field(None, description="Optional start date.")
    due_date: Optional[date] = Field(None, description="Optional due date.")


class ProjectResponse(ProjectBase):
    """Project response model."""

    id: int = Field(..., description="Project id.")
    owner_id: int = Field(..., description="Owner (user) id.")
    created_at: datetime = Field(..., description="Creation timestamp (UTC).")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC).")

    model_config = {"from_attributes": True}


class ProjectListParams(BaseModel):
    """Query parameters for listing projects."""

    page: int = Field(1, ge=1, description="1-based page number.")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page.")
    sort_by: str = Field(
        "created_at",
        description="Field to sort by. Supported: created_at, updated_at, name, status, due_date.",
    )
    sort_dir: str = Field("desc", description="Sort direction: asc or desc.")
    client_id: Optional[int] = Field(None, description="Optional filter by client id.")
    status: Optional[str] = Field(None, description="Optional filter by status.")
