# digital-agency-client-management-dashboard-228739-228748

This repo is the **backend** workspace. The full app has three containers:
- `project_management_database` (PostgreSQL) – exposed on **port 5000**
- `project_management_backend` (FastAPI) – exposed on **port 3001**
- `project_management_frontend` (React) – dev server typically on **port 3000**

## Quick configuration alignment (important)

### Database connection (backend → DB)
Backend reads DB connection from environment variables with safe defaults matching the provided DB container:
- host: `localhost`
- port: `5000`
- db: `myapp`
- user: `appuser`
- password: `dbuser123`

See `project_management_backend/.env.example` for all variables.

### Frontend API base URL (frontend → backend)
Frontend reads backend base URL from:
- `REACT_APP_API_BASE_URL` (defaults to `http://localhost:3001`)

See `project_management_frontend/.env.example`.

### CORS (frontend → backend)
Backend CORS is configured via:
- `ALLOWED_ORIGINS` (comma-separated, or `*`)
- `ALLOWED_HEADERS`
- `ALLOWED_METHODS`
- `CORS_MAX_AGE`

Defaults allow typical local development (e.g. `http://localhost:3000`).

## End-to-end smoke checks (runbook)

Below are lightweight “happy path” checks. You can do them via UI (preferred) or curl.

### 1) Auth: register → login → me
Assuming backend is running at `http://localhost:3001`:

```bash
curl -sS -X POST http://localhost:3001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

TOKEN=$(curl -sS -X POST http://localhost:3001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -sS http://localhost:3001/auth/me -H "Authorization: Bearer $TOKEN"
```

### 2) Clients CRUD (+ CSV export in UI)
- UI: Clients → “New Client” → Save → list updates → Edit → Save → Delete
- UI: Clients → “Export CSV” downloads `clients.csv`

Curl create/list example:
```bash
curl -sS -X POST http://localhost:3001/clients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme Corp","email":"contact@acme.com","phone":"+1-555-0100"}'

curl -sS "http://localhost:3001/clients?page=1&page_size=20&sort_by=created_at&sort_dir=desc" \
  -H "Authorization: Bearer $TOKEN"
```

### 3) Projects CRUD (with client association) (+ CSV export in UI)
- UI: Projects → “New Project” → pick Client → Save → verify filter by client/status
- UI: Projects → “Export CSV” downloads `projects.csv`

Curl create/list example:
```bash
curl -sS -X POST http://localhost:3001/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Website Redesign","status":"in_progress","client_id":1}'

curl -sS "http://localhost:3001/projects?status=in_progress&sort_by=due_date&sort_dir=asc" \
  -H "Authorization: Bearer $TOKEN"
```

### 4) Dashboard analytics
- UI: Dashboard should show counts and recent clients/projects.

Curl example:
```bash
curl -sS "http://localhost:3001/dashboard/analytics?recent_limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

### 5) Settings: theme persistence
- UI: Settings → set Light/Dark → refresh → preference should persist (stored via backend `/settings`).

Curl example:
```bash
curl -sS http://localhost:3001/settings -H "Authorization: Bearer $TOKEN"

curl -sS -X PUT http://localhost:3001/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme":"dark"}'
```