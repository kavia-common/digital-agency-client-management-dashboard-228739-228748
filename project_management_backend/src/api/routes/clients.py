from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.schemas.clients import ClientCreate, ClientResponse, ClientUpdate
from src.auth.jwt import get_current_user
from src.db.models import Client, User
from src.db.session import get_db

router = APIRouter(prefix="/clients", tags=["clients"])


def _apply_sorting(query, *, sort_by: str, sort_dir: str):
    """Apply basic sorting to a SQLAlchemy query.

    We intentionally whitelist allowed sort fields to prevent SQL injection via field names.
    """
    sort_map = {
        "created_at": Client.created_at,
        "updated_at": Client.updated_at,
        "name": Client.name,
    }
    sort_col = sort_map.get(sort_by, Client.created_at)
    direction = (sort_dir or "desc").lower()
    return query.order_by(asc(sort_col) if direction == "asc" else desc(sort_col))


@router.get(
    "",
    response_model=List[ClientResponse],
    summary="List clients",
    description="List clients owned by the current user with pagination and basic sorting.",
    operation_id="clients_list",
)
def list_clients(
    page: int = Query(1, ge=1, description="1-based page number."),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page."),
    sort_by: str = Query("created_at", description="Sort field: created_at, updated_at, name."),
    sort_dir: str = Query("desc", description="Sort direction: asc or desc."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ClientResponse]:
    """List clients owned by the current user."""
    query = db.query(Client).filter(Client.owner_id == current_user.id)
    query = _apply_sorting(query, sort_by=sort_by, sort_dir=sort_dir)

    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return [ClientResponse.model_validate(c) for c in items]


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Get client",
    description="Fetch a single client by id (must be owned by current user).",
    operation_id="clients_get",
)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    """Get a client by id with ownership check."""
    client = (
        db.query(Client)
        .filter(Client.id == client_id)
        .filter(Client.owner_id == current_user.id)
        .first()
    )
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return ClientResponse.model_validate(client)


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create client",
    description="Create a new client owned by the current user.",
    operation_id="clients_create",
)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    """Create a client for the current user."""
    client = Client(owner_id=current_user.id, **payload.model_dump())
    db.add(client)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # Most common: unique constraint owner_id+name
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Client already exists") from e

    db.refresh(client)
    return ClientResponse.model_validate(client)


@router.put(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Update client",
    description="Update an existing client (must be owned by current user).",
    operation_id="clients_update",
)
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    """Update a client by id with ownership check."""
    client = (
        db.query(Client)
        .filter(Client.id == client_id)
        .filter(Client.owner_id == current_user.id)
        .first()
    )
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Client update conflicts with existing data") from e

    db.refresh(client)
    return ClientResponse.model_validate(client)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete client",
    description="Delete a client (must be owned by current user). Deleting a client also deletes its projects.",
    operation_id="clients_delete",
)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Delete a client by id with ownership check."""
    client = (
        db.query(Client)
        .filter(Client.id == client_id)
        .filter(Client.owner_id == current_user.id)
        .first()
    )
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    db.delete(client)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
