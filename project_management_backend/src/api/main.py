import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.auth import router as auth_router
from src.api.routes.clients import router as clients_router
from src.api.routes.dashboard import router as dashboard_router
from src.api.routes.projects import router as projects_router
from src.api.routes.settings import router as settings_router
from src.db.init_db import init_db

openapi_tags = [
    {
        "name": "health",
        "description": "Service health and basic diagnostics.",
    },
    {
        "name": "auth",
        "description": "Authentication endpoints (register/login) and current user lookup using JWT Bearer tokens.",
    },
    {
        "name": "clients",
        "description": "CRUD endpoints for managing clients (owned per authenticated user).",
    },
    {
        "name": "projects",
        "description": "CRUD endpoints for managing projects (owned per authenticated user), optionally linked to clients.",
    },
    {
        "name": "dashboard",
        "description": "Dashboard analytics endpoints (counts and recent items), scoped to the authenticated user.",
    },
    {
        "name": "settings",
        "description": "Per-user settings endpoints (currently theme preference), scoped to the authenticated user.",
    },
]

app = FastAPI(
    title="Project Management Backend API",
    description=(
        "Backend API for the client project management dashboard.\n\n"
        "Authentication uses JWT tokens. Send requests with:\n"
        "`Authorization: Bearer <access_token>`."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)


def _split_env_csv(value: str) -> list[str]:
    """Split a comma-separated env var into a list of stripped, non-empty strings."""
    return [v.strip() for v in (value or "").split(",") if v.strip()]


# CORS configuration
#
# Default is dev-friendly and allows typical local frontend + this backend port.
# In hosted environments the orchestrator can set ALLOWED_ORIGINS accordingly.
_allowed_origins = _split_env_csv(
    os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001",
    )
)
_allowed_methods = _split_env_csv(os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,PATCH,OPTIONS")) or ["*"]
_allowed_headers = _split_env_csv(os.getenv("ALLOWED_HEADERS", "Content-Type,Authorization,X-Requested-With")) or ["*"]
_max_age = int(os.getenv("CORS_MAX_AGE", "3600"))

app.add_middleware(
    CORSMiddleware,
    # If explicitly set to "*" (or empty), allow all; otherwise use list.
    allow_origins=["*"] if (not _allowed_origins or _allowed_origins == ["*"]) else _allowed_origins,
    allow_credentials=True,
    allow_methods=_allowed_methods,
    allow_headers=_allowed_headers,
    max_age=_max_age,
)


@app.on_event("startup")
def _startup() -> None:
    """Initialize DB schema required for the backend on startup."""
    init_db()


@app.get("/", tags=["health"], summary="Health check", operation_id="health_check")
def health_check():
    """Health check endpoint used by deployment and monitoring."""
    return {"message": "Healthy"}


app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(projects_router)
app.include_router(dashboard_router)
app.include_router(settings_router)
