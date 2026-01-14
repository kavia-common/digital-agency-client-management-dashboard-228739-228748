# digital-agency-client-management-dashboard-228739-228748

## Backend Auth (FastAPI + JWT)

Base URL (backend): `http://localhost:<backend-port>`

### Endpoints

#### Register
`POST /auth/register`

Body:
```json
{ "email": "user@example.com", "password": "password123" }
```

Response:
```json
{ "id": 1, "email": "user@example.com" }
```

#### Login
`POST /auth/login`

Body:
```json
{ "email": "user@example.com", "password": "password123" }
```

Response:
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

#### Current user
`GET /auth/me`

Header:
`Authorization: Bearer <jwt>`

Response:
```json
{ "id": 1, "email": "user@example.com" }
```

### Environment variables

The backend supports these variables (optional; defaults match the provided database container details):

- `DB_HOST` (default: `localhost`)
- `DB_PORT` (default: `5000`)
- `DB_NAME` (default: `myapp`)
- `DB_USER` (default: `appuser`)
- `DB_PASSWORD` (default: `dbuser123`)
- `DATABASE_URL` (optional override, e.g. `postgresql+psycopg2://user:pass@host:port/db`)
- `JWT_SECRET_KEY` (recommended to set in production)
- `JWT_ALGORITHM` (default: `HS256`)
- `JWT_EXPIRES_MINUTES` (default: `60`)

## Clients & Projects (CRUD) - example curl

Assuming backend is running at `http://localhost:<backend-port>`.

1) Register + login:
```bash
curl -sS -X POST http://localhost:<backend-port>/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

TOKEN=$(curl -sS -X POST http://localhost:<backend-port>/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

2) Create a client:
```bash
curl -sS -X POST http://localhost:<backend-port>/clients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme Corp","email":"contact@acme.com","phone":"+1-555-0100"}'
```

3) List clients:
```bash
curl -sS "http://localhost:<backend-port>/clients?page=1&page_size=20&sort_by=created_at&sort_dir=desc" \
  -H "Authorization: Bearer $TOKEN"
```

4) Create a project (optionally tied to a client_id):
```bash
curl -sS -X POST http://localhost:<backend-port>/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Website Redesign","status":"in_progress","client_id":1}'
```

5) List projects (with filters):
```bash
curl -sS "http://localhost:<backend-port>/projects?status=in_progress&sort_by=due_date&sort_dir=asc" \
  -H "Authorization: Bearer $TOKEN"
```

## Dashboard analytics - example curl

Get counts + recent items for the authenticated user:
```bash
curl -sS "http://localhost:<backend-port>/dashboard/analytics?recent_limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

Example response:
```json
{
  "counts": {
    "total_clients": 3,
    "total_projects": 7,
    "projects_by_status": { "planned": 2, "in_progress": 3, "completed": 2 }
  },
  "recent_clients": [{ "id": 12, "name": "Acme Corp", "created_at": "2026-01-14T06:10:00Z" }],
  "recent_projects": [{ "id": 55, "name": "Website Redesign", "status": "in_progress", "created_at": "2026-01-14T06:12:00Z" }]
}
```

## User settings (theme) - example curl

1) Get current settings:
```bash
curl -sS "http://localhost:<backend-port>/settings" \
  -H "Authorization: Bearer $TOKEN"
```

2) Update theme (light/dark):
```bash
curl -sS -X PUT "http://localhost:<backend-port>/settings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme":"dark"}'
```