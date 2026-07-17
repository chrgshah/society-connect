# Neighborhood Library

Neighborhood Library is a browser-based system for managing a small library or
community book collection. It replaces paper registers and spreadsheets with one
place to manage members, books, borrowing, returns, availability, and overdue
records.

## What the product does

- Maintains a searchable member directory.
- Stores books, authors, categories, shelf locations, and copy counts.
- Records which member borrowed a book and when it is due.
- Restores availability automatically when a book is returned.
- Shows current lending history and overdue records.
- Provides dashboard totals for books, copies, members, and overdue borrowings.
- Protects staff access with cookie-based JWT authentication and CSRF validation.

The interface is intended for library staff or society administrators. Members do
not need to operate the application themselves.

## Application architecture

```text
Browser
  |
  | http://localhost:5173
  v
React + TypeScript + Ant Design
  |
  | JSON API, JWT cookies, CSRF header
  v
Django REST Framework :8000
  |                         |
  | persistent data         | login sessions
  v                         v
PostgreSQL :5432          Redis :6379
```

The repository is organized as follows:

```text
core/                 Authentication, sessions, middleware, exceptions, responses
services/controllers/ HTTP/API endpoints
services/factories/   Business rules and database operations
services/models/      PostgreSQL data models
services/serializers/ Request validation and response serialization
frontend/src/         React user interface
tests/                Backend unit and API integration tests
society_connect/      Django project and environment settings
docker/               Container startup scripts
```

## Technology

- Backend: Python, Django 4.2, Django REST Framework
- Frontend: React 18, TypeScript, Vite, Ant Design
- Data: PostgreSQL 16 and Redis 7
- Quality: pytest, coverage, Ruff, Bandit, pre-commit
- Runtime: Docker Compose or a local Python/Node installation

Docker installs the minimal runtime dependencies from `requirements-prod.txt`.
Local development and quality tools are listed in `requirements.txt`.

## Fastest installation: Docker

This is the recommended option for non-technical users and new developers because
it starts every required service with one command.

### Requirements

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and make
sure it is running.

### Start the application

From the repository directory, run:

```bash
docker compose up --build
```

Wait until the backend reports that Gunicorn is listening. Then open:

- Application: http://localhost:5173
- Backend API: http://localhost:8000/api/v1/
- Health check: http://localhost:8000/api/v1/health/
- Django admin: http://localhost:8000/admin/

Every backend startup applies migrations and loads the checked-in category fixture,
so the book form has Fiction, Science, History, Mystery, and Biography available.
The fixture uses stable identifiers and can safely be loaded again after a container
restart.

Docker does not create an application user. Create one with:

```bash
docker compose exec backend python manage.py shell
```

Then enter:

```python
from services.models.user import User
User.objects.create_user(
    username="admin",
    email="admin@example.com",
    password="Choose-A-Strong-Password",
)
exit()
```

Use that username and password on the login page.

### Useful Docker commands

```bash
# Start in the background
docker compose up --build -d

# View logs
docker compose logs -f

# Stop containers without deleting data
docker compose down

# Stop and permanently delete the local database volume
docker compose down --volumes

# Apply migrations manually
docker compose exec backend python manage.py migrate

# Reload the default book categories manually
docker compose exec backend python manage.py loaddata 2_categories

# Open a Django shell
docker compose exec backend python manage.py shell
```

`docker compose down --volumes` deletes local application data and cannot be
undone unless it was backed up.

## Developer installation without Docker

Use this option when actively developing and debugging services on the host.

### Requirements

- Python 3.9 or newer
- Node.js 20 or newer
- PostgreSQL
- Redis

### 1. Configure and start PostgreSQL and Redis

The checked-in Compose file can run only the infrastructure:

```bash
docker compose up -d db redis
```

The Docker database defaults are:

```text
Database: library_db
User:     library_user
Password: library_pass
Host:     localhost
Port:     5432
```

Update `society_connect/settings/dev.py` to match those values, or configure it for
your existing PostgreSQL installation. `dev.py` is intentionally ignored by Git so
each developer can maintain local credentials.

Create it from the checked-in template before starting Django:

```bash
cp society_connect/settings/dev.sample.py society_connect/settings/dev.py
```

### 2. Install the backend

```bash
python3 -m venv society-connect-env
source society-connect-env/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pre-commit install
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

On Windows PowerShell, activate the environment with:

```powershell
society-connect-env\Scripts\Activate.ps1
```

Keep the backend terminal running.

## Learning gRPC with the login API

The project includes one intentionally small gRPC API so developers can compare
gRPC with the existing REST login without changing the browser application. Both
transports reuse `LoginSerializer` for credential validation and
`AuthenticationFactory` for JWT creation:

```text
REST client -> POST /api/v1/auth/login/ -> LoginSerializer -> AuthenticationFactory
gRPC client -> AuthenticationService/Login -> LoginSerializer -> AuthenticationFactory
```

REST returns JWTs as HTTP-only cookies. gRPC has no browser-cookie convention, so
the learning API returns the access and refresh tokens as typed protobuf fields.
Treat those values as secrets and do not paste them into logs or commit them.

### Run it locally without Docker

PostgreSQL and Redis must be available using the values in the existing
`society_connect/settings/dev.py`. Activate the same environment used for Django,
install the updated requirements, and apply migrations:

```bash
source /Users/chiragshah/Projects/environments/society-connect-env/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

Start only the gRPC server in one terminal (the REST server does not need to run):

```bash
python manage.py run_grpc_server
```

It listens on `127.0.0.1:50051` by default. In a second terminal, activate the
same environment and call the generated gRPC client. The command prompts for the
password without saving it in shell history:

```bash
python manage.py grpc_login admin
```

For the sample local administrator, enter `Admin@12345` when prompted. A successful
response shows the user and both JWTs. Stop the server with `Ctrl+C`.

Useful alternatives are:

```bash
# Use another local port
python manage.py run_grpc_server --port 50052
python manage.py grpc_login admin --address 127.0.0.1:50052

# Run only the gRPC tests
python3 -m pytest tests/test_grpc_authentication.py -v
```

The contract lives in `services/grpc_api/authentication.proto`. The generated
`authentication_pb2.py` contains message classes, while
`authentication_pb2_grpc.py` contains the client stub and server base class. After
changing the contract, regenerate both checked-in files from the repository root:

```bash
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  services/grpc_api/authentication.proto
```

This server uses an insecure local channel to keep the exercise focused. Bind it
only to localhost. A production/public gRPC service must use TLS, secret
management, rate limiting, monitoring, and a deliberate token-storage strategy.

### 3. Install the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

The frontend uses `http://localhost:8000/api/v1` by default. To change it, copy
`frontend/.env.example` to `frontend/.env` and edit `VITE_API_BASE_URL`.

## Environment configuration

Important backend variables are:

| Variable | Purpose | Docker development value |
| --- | --- | --- |
| `ENVIRONMENT` | Selects `dev`, `stage`, or `prod` settings | `prod` |
| `SECRET_KEY` | Signs Django and JWT data | Docker-only placeholder |
| `ALLOWED_HOSTS` | Hosts Django accepts | `localhost,127.0.0.1,backend` |
| `FRONTEND_ORIGINS` | CORS and CSRF browser origins | Local Vite origins |
| `POSTGRES_DB` | PostgreSQL database | `library_db` |
| `POSTGRES_USER` | PostgreSQL user | `library_user` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `library_pass` |
| `POSTGRES_HOST` | PostgreSQL service hostname | `db` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `REDIS_URL` | Authentication session store | `redis://redis:6379/0` |
| `REDIS_SESSION_TTL_SECONDS` | Maximum lifetime of each authentication session | `21600` (6 hours) |

The Compose credentials are for local use only. Replace the secret key, database
password, allowed hosts, and origin values before deploying anywhere public. Keep
secure-cookie settings enabled when using HTTPS.

## Testing and quality checks

The test suite uses the existing development settings and its configured
PostgreSQL server.

```bash
# Run all backend tests
python3 -m pytest

# Run tests with the enforced 99% minimum coverage
python3 -m pytest \
  --cov=core \
  --cov=services \
  --cov-report=term-missing \
  --cov-fail-under=99

# Run all commit checks manually
pre-commit run --all-files

# Run only the security scan
pre-commit run bandit --all-files

# Verify the frontend production build
cd frontend && npm run build
```

Every commit runs tests and the 99% coverage gate, Ruff linting/formatting, Bandit
security analysis, and basic file checks. If Ruff reformats files, review them,
stage the changes again, and retry the commit.

## Common problems

### The backend cannot connect to PostgreSQL

Confirm PostgreSQL is running and the database values in `dev.py` are correct:

```bash
docker compose ps
docker compose logs db
```

### The backend image fails while installing Python packages

Rebuild the backend with plain progress output to reveal the exact package error:

```bash
docker compose build backend --no-cache --progress=plain
docker compose up
```

The backend image uses `requirements-prod.txt`, which intentionally excludes local
development tools such as IPython, pytest, and pre-commit.

### A commit says `No module named pytest`

Activate the project virtual environment and install all requirements:

```bash
source society-connect-env/bin/activate
pip install -r requirements.txt
```

### Authentication works in Docker but not in the browser

Confirm the frontend URL appears in `FRONTEND_ORIGINS`. Plain HTTP local setups
must use `CSRF_COOKIE_SECURE=false` and `JWT_COOKIE_SECURE=false`; public HTTPS
deployments should keep both values true.

### Reset the Docker database

```bash
docker compose down --volumes
docker compose up --build
```

This permanently removes local members, books, and lending records.
