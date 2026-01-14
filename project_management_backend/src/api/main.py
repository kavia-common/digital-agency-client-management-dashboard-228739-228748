from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.auth import router as auth_router
from src.api.routes.clients import router as clients_router
from src.api.routes.projects import router as projects_router
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

# Keep CORS permissive for local dev; frontend will use Authorization: Bearer tokens.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
