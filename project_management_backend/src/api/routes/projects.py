from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from src.api.schemas.projects import ProjectCreate, ProjectResponse, ProjectUpdate
from src.auth.jwt import get_current_user
from src.db.models import Client, Project, User
from src.db.session import get_db

router = APIRouter(prefix="/projects", tags=["projects"])

_ALLOWED_PROJECT_SORTS = {
    "created_at": Project.created_at,
    "updated_at": Project.updated_at,
    "name": Project.name,
    "status": Project.status,
    "due_date": Project.due_date,
}


def _apply_sorting(query, *, sort_by: str, sort_dir: str):
    """Apply whitelisted sorting to a projects query."""
    sort_col = _ALLOWED_PROJECT_SORTS.get(sort_by, Project.created_at)
    direction = (sort_dir or "desc").lower()
    return query.order_by(asc(sort_col) if direction == "asc" else desc(sort_col))


def _validate_client_ownership(db: Session, *, current_user_id: int, client_id: Optional[int]) -> None:
    """Validate that a provided client_id exists and is owned by the current user."""
    if client_id is None:
        return

    client = db.query(Client).filter(Client.id == client_id, Client.owner_id == current_user_id).first()
    if client is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid client_id (not found or not owned)")


@router.get(
    "",
    response_model=List[ProjectResponse],
    summary="List projects",
    description="List projects owned by the current user with pagination, basic sorting, and optional filters.",
    operation_id="projects_list",
)
def list_projects(
    page: int = Query(1, ge=1, description="1-based page number."),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page."),
    sort_by: str = Query("created_at", description="Sort field: created_at, updated_at, name, status, due_date."),
    sort_dir: str = Query("desc", description="Sort direction: asc or desc."),
    client_id: Optional[int] = Query(None, description="Optional filter by client id."),
    status_filter: Optional[str] = Query(None, alias="status", description="Optional filter by status."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ProjectResponse]:
    """List projects owned by the current user."""
    query = db.query(Project).filter(Project.owner_id == current_user.id)

    if client_id is not None:
        query = query.filter(Project.client_id == client_id)

    if status_filter is not None:
        query = query.filter(Project.status == status_filter)

    query = _apply_sorting(query, sort_by=sort_by, sort_dir=sort_dir)
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return [ProjectResponse.model_validate(p) for p in items]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project",
    description="Fetch a single project by id (must be owned by current user).",
    operation_id="projects_get",
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    """Get a project by id with ownership check."""
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .filter(Project.owner_id == current_user.id)
        .first()
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
    description="Create a new project owned by the current user. If client_id is set, the client must be owned by the user.",
    operation_id="projects_create",
)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    """Create a project with optional client association."""
    _validate_client_ownership(db, current_user_id=current_user.id, client_id=payload.client_id)

    project = Project(owner_id=current_user.id, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Update an existing project (must be owned by current user). If client_id is set, the client must be owned by the user.",
    operation_id="projects_update",
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    """Update a project by id with ownership check."""
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .filter(Project.owner_id == current_user.id)
        .first()
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    update_data = payload.model_dump(exclude_unset=True)

    # Validate client ownership if client_id is being changed.
    if "client_id" in update_data:
        _validate_client_ownership(db, current_user_id=current_user.id, client_id=update_data.get("client_id"))

    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Delete a project (must be owned by current user).",
    operation_id="projects_delete",
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Delete a project by id with ownership check."""
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .filter(Project.owner_id == current_user.id)
        .first()
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
