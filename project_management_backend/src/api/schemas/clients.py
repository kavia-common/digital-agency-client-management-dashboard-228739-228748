from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ClientBase(BaseModel):
    """Shared fields for client create/update payloads."""

    name: str = Field(..., min_length=1, max_length=200, description="Client display name.")
    email: Optional[str] = Field(None, max_length=320, description="Optional client contact email.")
    phone: Optional[str] = Field(None, max_length=50, description="Optional client contact phone.")
    company: Optional[str] = Field(None, max_length=200, description="Optional company/organization name.")
    notes: Optional[str] = Field(None, max_length=5000, description="Optional free-form notes about the client.")


class ClientCreate(ClientBase):
    """Payload to create a client."""


class ClientUpdate(BaseModel):
    """Payload to update a client (partial update semantics)."""

    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Client display name.")
    email: Optional[str] = Field(None, max_length=320, description="Optional client contact email.")
    phone: Optional[str] = Field(None, max_length=50, description="Optional client contact phone.")
    company: Optional[str] = Field(None, max_length=200, description="Optional company/organization name.")
    notes: Optional[str] = Field(None, max_length=5000, description="Optional free-form notes about the client.")


class ClientResponse(ClientBase):
    """Client response model."""

    id: int = Field(..., description="Client id.")
    owner_id: int = Field(..., description="Owner (user) id.")
    created_at: datetime = Field(..., description="Creation timestamp (UTC).")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC).")

    model_config = {"from_attributes": True}


class ClientListParams(BaseModel):
    """Query parameters for listing clients."""

    page: int = Field(1, ge=1, description="1-based page number.")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page.")
    sort_by: str = Field(
        "created_at",
        description="Field to sort by. Supported: created_at, updated_at, name.",
    )
    sort_dir: str = Field("desc", description="Sort direction: asc or desc.")
