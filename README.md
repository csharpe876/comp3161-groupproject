# COMP3161 — Course Management System

Full-stack course management platform built for the COMP3161 final project.

## Tech Stack

| Layer | Technology |
|---|---|
| Database | PostgreSQL 16 |
| Backend API | Python 3.12 · Flask 3 · psycopg2 (raw SQL, no ORM) |
| Auth | JWT (flask-jwt-extended) · bcrypt |
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS |
| Infrastructure | Docker · Docker Compose · Nginx |

---

## Architecture — MVC

The backend follows a strict MVC pattern:

- **Models** (`backend/models/`) — all database queries live here, one file per domain
- **Controllers** (`backend/routes/`) — thin Flask blueprints that parse requests, authorise, call models, return JSON
- **Views** — JSON responses via `flask.jsonify`

```
backend/
├── app.py               Application factory + blueprint registration
├── config.py            Environment-based config
├── db.py                psycopg2 connection pool + query helpers
├── models/              Model layer (all SQL)
│   ├── user.py          Users table operations
│   ├── course.py        Courses + Enrollment operations
│   ├── assignment.py    Assignments, Submissions, Grades
│   ├── forum.py         Forums, Threads, Replies (recursive CTE)
│   ├── content.py       ContentSections + CourseContent
│   ├── calendar.py      CalendarEvents
│   └── report.py        Report view queries
└── routes/              Controller layer (HTTP handlers only)
    ├── auth.py
    ├── courses.py
    ├── assignments.py
    ├── forums.py
    ├── content.py
    ├── calendar.py
    └── reports.py
```

---

## Project Structure

```
├── backend/
├── database/
│   ├── schema.sql        CREATE TABLE statements (11 tables)
│   ├── views.sql         5 report views
│   └── indexes.sql       Performance indexes
├── frontend/             React SPA (Vite + TypeScript + Tailwind)
│   ├── nginx.conf        Nginx config (gzip, CSP headers, SPA fallback, API proxy)
│   └── src/
│       ├── pages/        Login, Register, Dashboard, CourseDetail,
│       │                 ForumDetail, ThreadDetail, AdminPanel
│       ├── components/   Layout, Navbar, ProtectedRoute, ReplyThread
│       ├── context/      AuthContext (JWT storage)
│       └── services/     Axios instance with JWT interceptor
├── nginx/nginx.conf      Standalone reverse proxy config (alternative deployment)
├── docker-compose.yml
├── insertdata.py         Seed-data generator
├── project_insert_data.sql  Pre-generated seed data (auto-loaded on first start)
└── test_users.sql        Pre-seeded test accounts (auto-loaded on first start)
```

---

## Quick Start (Docker — recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)

### Steps

```bash
# 1. Clone the repo
git clone <repo-url>
cd comp3161-groupproject

# 2. Configure environment
cp .env.example .env
```

Edit `.env` — the defaults work for local development, but set a real `JWT_SECRET_KEY` for any shared deployment:

```env
POSTGRES_DB=comp3161-group_project
POSTGRES_USER=project_user
POSTGRES_PASSWORD=your-db-password

# Full connection string used by the backend (db = docker service name)
DATABASE_URL=postgresql://project_user:your-db-password@db:5432/comp3161-group_project

# Generate a real key: python -c "import secrets; print(secrets.token_hex(48))"
JWT_SECRET_KEY=change-me-to-a-long-random-secret

FLASK_ENV=production
```

```bash
# 3. Build and start all services
docker compose up -d --build

# 4. Open the app
start http://localhost        # Windows
open http://localhost         # macOS
```

### What happens on first start

Docker automatically runs the following init scripts against the database in order:

| Order | File | Purpose |
|---|---|---|
| 01 | `database/schema.sql` | Creates all 11 tables |
| 02 | `database/views.sql` | Creates 5 report views |
| 03 | `database/indexes.sql` | Creates performance indexes |
| 04 | `test_users.sql` | Inserts the 3 test accounts |
| 05 | `project_insert_data.sql` | Inserts full dataset |

> The initial seed load can take a minute or two. Monitor with `docker compose logs -f db`.

### Useful commands

```bash
# View logs
docker compose logs -f                      # all services
docker compose logs -f backend              # Flask API only

# Check container health
docker compose ps

# Stop everything
docker compose down

# Stop and wipe the database volume (full reset)
docker compose down -v

# Rebuild after code changes
docker compose up -d --build
```

### PostgreSQL direct access

The database is exposed on port **5433** (avoids conflict with a local Postgres):

```bash
psql -h localhost -p 5433 -U project_user -d comp3161-group_project
```

---

## Test Accounts

Three accounts are seeded automatically on first start:

| UserID | Password | Role |
|---|---|---|
| `test_student` | `password123` | Student |
| `test_lecturer` | `password123` | Lecturer |
| `test_admin` | `password123` | Admin |

Use these on the Login page or via `POST /api/auth/login`.

> **Note:** Bulk-seeded users have SHA-256 hashed passwords and cannot log in via the API. Use the test accounts above or register a new account.

---

## Re-generating Seed Data

```bash
pip install faker
python insertdata.py   # overwrites project_insert_data.sql

# Reload into a running container
docker exec -i comp3161-groupproject-db-1 \
  psql -U project_user -d comp3161-group_project < project_insert_data.sql
```

---

## API Reference

All protected endpoints require `Authorization: Bearer <token>` header.

### Auth
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | — | Create account |
| POST | `/api/auth/login` | — | Returns JWT token |
| GET | `/api/health` | — | Health check |

### Courses
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses` | — | All courses |
| GET | `/api/courses/<id>` | JWT | Course detail |
| POST | `/api/courses` | Admin | Create course |
| GET | `/api/students/<id>/courses` | JWT | Student's enrolled courses |
| GET | `/api/lecturers/<id>/courses` | JWT | Lecturer's courses |
| POST | `/api/courses/<id>/enroll` | Student/Admin | Enrol in course |
| POST | `/api/courses/<id>/assign-lecturer` | Admin | Assign lecturer |
| GET | `/api/courses/<id>/members` | JWT | Course roster |

### Calendar
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses/<id>/events` | JWT | All events for a course |
| POST | `/api/courses/<id>/events` | Lecturer/Admin | Create event |
| GET | `/api/students/<id>/events?date=YYYY-MM-DD` | JWT | Student events on a date |

### Forums & Threads
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses/<id>/forums` | JWT | All forums in a course |
| POST | `/api/courses/<id>/forums` | Lecturer/Admin | Create forum |
| GET | `/api/forums/<id>/threads` | JWT | Threads in a forum |
| POST | `/api/forums/<id>/threads` | JWT | Post a new thread |
| GET | `/api/threads/<id>` | JWT | Thread + full reply tree |
| POST | `/api/threads/<id>/replies` | JWT | Reply to thread |
| POST | `/api/replies/<id>/replies` | JWT | Nested reply |

### Course Content
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses/<id>/content` | JWT | Sections with nested content items |
| POST | `/api/courses/<id>/sections` | Lecturer/Admin | Add a section |
| POST | `/api/sections/<id>/content` | Lecturer/Admin | Add a content item |

### Assignments & Grades
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses/<id>/assignments` | JWT | List assignments |
| POST | `/api/courses/<id>/assignments` | Lecturer/Admin | Create assignment |
| POST | `/api/assignments/<id>/submit` | Student | Submit work |
| GET | `/api/assignments/<id>/submissions` | JWT | View submissions |
| POST | `/api/submissions/<id>/grade` | Lecturer/Admin | Grade a submission |
| GET | `/api/students/<id>/average` | JWT | Student overall average |

### Reports (Admin/Lecturer only)
| Endpoint | Description |
|---|---|
| `GET /api/reports/courses-50plus` | Courses with ≥ 50 enrolled students |
| `GET /api/reports/students-5plus` | Students enrolled in ≥ 5 courses |
| `GET /api/reports/lecturers-3plus` | Lecturers teaching ≥ 3 courses |
| `GET /api/reports/top10-enrolled` | 10 most enrolled courses |
| `GET /api/reports/top10-averages` | Top 10 students by grade average |

---

## Local Development (without Docker)

### Backend

Requires a locally running PostgreSQL instance.

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt

# Point DATABASE_URL at your local Postgres in .env:
# DATABASE_URL=postgresql://project_user:password@localhost:5432/comp3161-group_project

flask --app app --debug run
```

### Frontend

```bash
cd frontend
npm install
npm run dev     # Vite dev server at http://localhost:5173
```

> In dev mode the frontend proxies `/api/*` to `http://localhost:5000` via `vite.config.ts`.

---

## Deployment (VPS / Internet)

```bash
# On any server with Docker installed:
git clone <repo-url>
cd comp3161-groupproject
cp .env.example .env
# Fill in strong values for POSTGRES_PASSWORD and JWT_SECRET_KEY
docker compose up -d --build
```

The app listens on port **80**. To add HTTPS:

1. Point your domain's A record at the server IP.
2. Install Certbot: `snap install certbot --classic`
3. Obtain a certificate and update `frontend/nginx.conf` with the `ssl_certificate` directives, then `docker compose up -d --build`.
