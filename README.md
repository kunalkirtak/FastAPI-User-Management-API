# FastAPI User Management API

A production-ready **CRUD API for user management**, built with **FastAPI**, **SQLAlchemy**, and **Pydantic** — designed as a portfolio-quality reference project showing clean architecture, validation, testing, and deployment practices.

> **Build status:** ✅ **All 4 parts complete.** Full CRUD, structured logging, request tracing, global error handling, Docker/Compose, Alembic migrations, and a 39-test pytest suite. See the [Roadmap](#roadmap) below for how it was built.

---

## Table of Contents

- [Roadmap](#roadmap)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Installation](#installation)
- [Running the API](#running-the-api)
- [Screenshots](#screenshots)
- [API Endpoints](#api-endpoints)
- [Observability](#observability)
- [Configuration](#configuration)
- [Database Migrations](#database-migrations)
- [Docker](#docker)
- [Testing](#testing)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Roadmap

This project is built incrementally, one production concern at a time:

| Part | Focus | Status |
|------|-------|--------|
| **1** | Project foundation — repo structure, config, database setup, app entrypoint | ✅ Done |
| **2** | Core application — models, schemas, CRUD layer, service layer, `/users` router | ✅ Done |
| **3** | Production features — logging, middleware, error handling, `/health` endpoint | ✅ Done |
| **4** | Deployment & quality — Docker, Docker Compose, Alembic migrations, unit tests, final docs | ✅ Done |

---

## Features

### CRUD
- [x] Create user
- [x] Read single user
- [x] Read all users (with basic pagination)
- [x] Update user (partial update)
- [x] Delete user

### Validation
- [x] Email validation (Pydantic `EmailStr`)
- [x] Username validation (length + alphanumeric/underscore)
- [x] Password validation (min length, letter + digit required)
- [x] Duplicate email prevention (409 Conflict)
- [x] Duplicate username prevention (409 Conflict)

### Database
- [x] SQLAlchemy ORM engine/session configured
- [x] SQLite by default (zero setup to run locally)
- [x] Config designed for a one-line swap to PostgreSQL

### FastAPI Features
- [x] Environment-driven configuration (`pydantic-settings`)
- [x] Auto Swagger UI (`/docs`) and ReDoc (`/redoc`)
- [x] CORS middleware
- [x] Dependency injection for DB sessions (`Depends(get_db)`) and pagination (`Depends(get_pagination_params)`)
- [x] Response models / request validation (`schemas.py`)
- [x] HTTP status codes (200, 201, 204, 404, 409, 422, 500, 503)
- [x] Centralized/global exception handling (validation, DB integrity, and catch-all)

### Professional Features
- [x] `.env` based configuration with `Settings` class
- [x] Type hinting throughout
- [x] Clean architecture (router → service → CRUD → ORM)
- [x] Password hashing (`passlib` + `bcrypt`) — plaintext passwords are never stored
- [x] Structured logging (`app/utils/logger.py`), configured once at startup
- [x] Custom middleware (`RequestLoggingMiddleware` — request id + timing on every call)
- [x] Unit tests (39 tests across `test_database.py`, `test_users.py`, `test_api.py`)

### Production Ready
- [x] Docker / Docker Compose (SQLite by default, optional PostgreSQL profile)
- [x] Alembic migrations (auto-generated initial revision, tested upgrade/downgrade)
- [x] API versioning prefix configured (`/api/v1`)
- [x] Health check endpoint (`GET /health`, checks DB connectivity, returns 503 when degraded)

---

## Tech Stack

| Category | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org/) |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) / pydantic-settings |
| Server | [Uvicorn](https://www.uvicorn.org/) |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) |
| Database | SQLite (dev) → PostgreSQL (production) |
| Testing | [Pytest](https://docs.pytest.org/) + httpx + pytest-cov |
| Containerization | Docker / Docker Compose |
| Password hashing | passlib + bcrypt |
| Auth (planned) | python-jose (JWT) — see Future Improvements |

---

## Folder Structure

Final structure of the completed project:

```
FastAPI-User-Management-API/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app instance & startup
│   ├── database.py              # SQLAlchemy engine/session/get_db
│   ├── dependencies.py          # Shared dependencies (pagination, request id)
│   ├── config.py                # Environment-driven settings
│   │
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py                # Pydantic request/response schemas
│   ├── crud.py                   # Database access layer
│   │
│   ├── routers/
│   │     ├── users.py            # /users endpoints
│   │     └── health.py           # /health endpoint (DB connectivity check)
│   │
│   ├── services/
│   │     └── user_service.py     # Business logic layer (hashing, duplicate checks, 404s)
│   │
│   ├── utils/
│   │     ├── validators.py       # Reusable validation rules (username/password)
│   │     ├── logger.py           # Logging configuration
│   │     └── helpers.py          # Misc helpers (request ids, UTC time, email masking)
│   │
│   └── middleware/
│         └── request_logger.py   # Request-id + timing middleware
│
├── tests/
│     ├── conftest.py             # Isolated test DB, TestClient, shared fixtures
│     ├── test_database.py        # Engine/session-level tests
│     ├── test_users.py           # CRUD + service-layer unit tests
│     └── test_api.py             # End-to-end HTTP tests (every endpoint + error path)
│
├── alembic/                      # Migration environment
│     ├── env.py                  # Wired to app.config.settings + app.models
│     ├── script.py.mako
│     └── versions/
│           └── ..._create_users_table.py
│
├── docs/
│     └── requests.http           # Sample requests (VS Code REST Client, or read as reference)
│
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── LICENSE
└── pyproject.toml
```

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/FastAPI-User-Management-API.git
cd FastAPI-User-Management-API

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # macOS / Linux
venv\Scripts\activate             # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# then edit .env if you want to change any defaults
```

---

## Running the API

### Option A — locally with uvicorn

```bash
uvicorn app.main:app --reload
```

### Option B — with Docker Compose (SQLite, zero config)

```bash
cp .env.example .env
docker compose up --build
```

### Option C — with Docker Compose + PostgreSQL

```bash
cp .env.example .env
# then set DATABASE_URL=postgresql://postgres:postgres@db:5432/users_db in .env
docker compose --profile postgres up --build
```

In all three cases the API will be available at:

- **App root:** http://127.0.0.1:8000/
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

On startup, `app/main.py` calls `Base.metadata.create_all()`, which will create the SQLite file automatically — no manual database setup required for local development. For anything beyond local dev, prefer Alembic migrations (see [Database Migrations](#database-migrations) below) so schema changes are tracked and reversible.

A ready-made `docs/requests.http` file has requests for every endpoint (including the error cases below) if you use an HTTP client that supports `.http` files, such as the VS Code REST Client extension.

### Sample response — `GET /`

```json
{
  "message": "Welcome to FastAPI User Management API",
  "version": "1.0.0",
  "environment": "development",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

## Screenshots

> Once the API is running locally, visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI. Add a screenshot to `docs/swagger-ui.png` and embed it here:
>
> `![Swagger UI](docs/swagger-ui.png)`

---

## API Endpoints

All user endpoints are mounted under the versioned prefix `API_V1_PREFIX` (default `/api/v1`), so upgrading the API later won't break existing clients.

```
GET     /                       -> Welcome message                    ✅
GET     /health                 -> Health check (DB connectivity)     ✅

POST    /api/v1/users           -> Create a user                      ✅
GET     /api/v1/users           -> List users (skip/limit pagination) ✅
GET     /api/v1/users/{id}      -> Get a single user                  ✅
PUT     /api/v1/users/{id}      -> Update a user (partial)            ✅
DELETE  /api/v1/users/{id}      -> Delete a user                      ✅
```

### Sample response — `GET /health`

```json
{
  "status": "ok",
  "database": "ok",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2026-07-15T11:37:52.826409+00:00"
}
```

If the database is unreachable, this returns `503 Service Unavailable` with `"status": "degraded"` instead — useful for load balancer / orchestrator health probes.

### Sample request — `POST /api/v1/users`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
        "username": "johndoe",
        "email": "johndoe@example.com",
        "full_name": "John Doe",
        "password": "S3curePass"
      }'
```

### Sample response — `201 Created`

```json
{
  "username": "johndoe",
  "email": "johndoe@example.com",
  "full_name": "John Doe",
  "id": 1,
  "is_active": true,
  "created_at": "2026-07-15T11:32:44.813924",
  "updated_at": "2026-07-15T11:32:44.813931"
}
```

Note that the password never appears in the response — only `hashed_password` is stored, and it's excluded from `UserResponse` entirely.

### Sample error responses

Duplicate email/username → `409 Conflict`:
```json
{ "detail": "A user with this email already exists" }
```

Unknown user id → `404 Not Found`:
```json
{ "detail": "User with id 9999 not found" }
```

Weak password (e.g. too short, or missing a digit) → `422 Unprocessable Entity`, with a structured, field-by-field validation error body.

An unexpected server-side error → `500 Internal Server Error` with a generic, safe message (the real exception and traceback are logged server-side, never sent to the client):
```json
{ "detail": "An unexpected error occurred. Please try again later." }
```

### List with pagination

```bash
curl "http://127.0.0.1:8000/api/v1/users?skip=0&limit=10"
```

---

## Observability

Every response includes two headers, added by `RequestLoggingMiddleware`:

| Header | Purpose |
|---|---|
| `X-Request-ID` | Unique id for this request. If the caller already sent this header (e.g. from an upstream gateway), it's reused; otherwise one is generated. Useful for correlating a client-side error with the matching server log line. |
| `X-Process-Time-Ms` | How long the server took to handle the request, in milliseconds. |

Console output looks like:

```
2026-07-15 11:37:53 | INFO     | app.request | request started  | id=1678466b... | POST /api/v1/users | client=testclient
2026-07-15 11:37:53 | INFO     | app.request | request finished | id=1678466b... | POST /api/v1/users | status=201 | 352.46ms
```

Log verbosity is controlled by the `LOG_LEVEL` environment variable.

---

## Configuration

All configuration lives in `app/config.py` and is populated from environment
variables (see `.env.example` for the full list). Key settings:

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/app.db` | Database connection string |
| `API_V1_PREFIX` | `/api/v1` | Prefix for versioned routes |
| `SECRET_KEY` | — | Reserved for JWT signing once auth is added (see Future Improvements) |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins |
| `DEBUG` | `False` | Enables SQL echo / verbose logging |
| `LOG_LEVEL` | `INFO` | Controls log verbosity (`DEBUG`, `INFO`, `WARNING`, ...) |

---

## Database Migrations

Schema changes are managed with **Alembic** rather than by hand-editing tables. The migration environment (`alembic/env.py`) reads `DATABASE_URL` from `app.config.settings` — the same source of truth the app itself uses — so migrations and the running app can never point at different databases by accident.

```bash
# Apply all pending migrations (creates the `users` table on a fresh DB)
alembic upgrade head

# Check which revision the database is currently on
alembic current

# See full migration history
alembic history

# After changing a model in app/models.py, generate a new migration:
alembic revision --autogenerate -m "add some_column to users"

# Review the generated file in alembic/versions/ before applying it, then:
alembic upgrade head

# Roll back one revision (or `alembic downgrade base` to undo everything)
alembic downgrade -1
```

The initial migration (`alembic/versions/..._create_users_table.py`) was generated with `--autogenerate` against `app/models.py` and has been verified to apply and roll back cleanly on SQLite (`render_as_batch=True` is set in `env.py` specifically so `ALTER TABLE`-style changes work on SQLite, which doesn't support most `ALTER` operations natively).

> **Note:** `app/main.py` still calls `Base.metadata.create_all()` on startup for local-dev convenience (so `uvicorn app.main:app --reload` works immediately on a fresh clone with zero setup). In a real deployment, run `alembic upgrade head` as a release step and treat Alembic as the source of truth for schema changes from then on.

---

## Docker

The `Dockerfile` builds a slim, non-root image with a stdlib-based `HEALTHCHECK` against `/health` (no extra OS packages needed). `docker-compose.yml` covers two setups:

### SQLite (default — zero extra config)

```bash
cp .env.example .env
docker compose up --build
```

The SQLite file lives at `data/app.db` inside a named volume (`sqlite_data`), so it survives `docker compose down` / container recreation. `app/database.py` creates that directory automatically — nothing to set up by hand.

### PostgreSQL

```bash
cp .env.example .env
# edit .env:
#   DATABASE_URL=postgresql://postgres:postgres@db:5432/users_db
docker compose --profile postgres up --build
```

This starts a `postgres:16-alpine` container alongside the API, with its own named volume (`postgres_data`) and a `pg_isready` healthcheck.

### Building/running without Compose

```bash
docker build -t fastapi-user-management-api .
docker run -p 8000:8000 --env-file .env fastapi-user-management-api
```

---

## Testing

39 tests, split by what they exercise:

| File | Covers |
|---|---|
| `tests/test_database.py` | The SQLAlchemy engine/session setup itself (`get_db`, table registration) |
| `tests/test_users.py` | `crud.py` + `services/user_service.py` directly — hashing, duplicate checks, 404s, partial updates |
| `tests/test_api.py` | Every endpoint end-to-end through `TestClient`, including every documented error case (409, 404, 422) |

Tests run against an isolated SQLite file in the OS temp directory (configured in `tests/conftest.py`, which sets `DATABASE_URL` **before** importing anything from `app`) — your local `data/app.db` is never touched by the test suite, and the schema is dropped/recreated before every single test so tests can't leak state into each other.

```bash
# Run the full suite
pytest

# Verbose output
pytest -v

# With a coverage report (91% at last count)
pytest --cov=app --cov-report=term-missing
```

---

## Future Improvements

- Search users by name
- Sorting and filtering on `GET /users` (basic `skip`/`limit` pagination is already in)
- JWT authentication (login endpoint using the existing `verify_password` helper, plus a `get_current_user` dependency in `app/dependencies.py`)
- Rate limiting
- OpenAPI customization (tags, examples, custom docs branding)
- CI (GitHub Actions running `pytest` + `alembic upgrade head` against a throwaway Postgres service on every PR)

---

## License

This project is licensed under the [MIT License](LICENSE).
