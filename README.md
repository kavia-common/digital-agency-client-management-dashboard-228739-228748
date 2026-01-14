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