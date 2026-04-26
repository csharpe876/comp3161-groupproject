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
| CI/CD | GitHub Actions |

---

## Project Structure

```
├── backend/              Flask REST API
│   ├── app.py            Application factory
│   ├── config.py         Environment-based config
│   ├── db.py             psycopg2 connection pool + helpers
│   └── routes/           Blueprints: auth, courses, calendar,
│                         forums, content, assignments, reports
├── database/
│   ├── schema.sql        CREATE TABLE statements
│   ├── views.sql         5 report views
│   └── indexes.sql       Performance indexes
├── frontend/             React SPA (Vite + TypeScript + Tailwind)
│   └── src/
│       ├── pages/        Login, Register, Dashboard, CourseDetail,
│       │                 ForumDetail, ThreadDetail, AdminPanel
│       ├── components/   Layout, Navbar, ProtectedRoute, ReplyThread
│       ├── context/      AuthContext (JWT storage)
│       └── services/     Axios instance with JWT interceptor
├── nginx/nginx.conf      Reverse proxy + SPA fallback
├── insertdata.py         Seed-data generator (100k students, 200 courses)
├── project_insert_data.sql  Pre-generated seed data (auto-loaded on first start)
├── test_users.sql        Pre-seeded test accounts (auto-loaded on first start)
├── docker-compose.yml
└── .github/workflows/ci.yml
```

---

## Quick Start (Docker)

```bash
# 1. Clone the repo
git clone <repo-url>
cd comp3161-groupproject

# 2. Configure environment
cp .env.example .env
```

Edit `.env` and set all required values:

```env
# PostgreSQL credentials (must match across all services)
POSTGRES_DB=comp3161-group_project
POSTGRES_USER=project_user
POSTGRES_PASSWORD=your-db-password

# Flask JWT secret — use a long random string in production
JWT_SECRET_KEY=change-me-to-a-long-random-secret

FLASK_ENV=production
```

```bash
# 3. Start all services (DB, backend, frontend, nginx)
docker compose up -d --build

# 4. Open http://localhost in your browser
```

On the **first start**, Docker automatically runs the following init scripts in order:
1. `database/schema.sql` — creates all tables
2. `database/views.sql` — creates report views
3. `database/indexes.sql` — creates indexes
4. `test_users.sql` — inserts pre-seeded test accounts
5. `project_insert_data.sql` — inserts full dataset (100k students, 200 courses, etc.)

> **Note:** The initial seed load can take a minute or two. Check `docker compose logs -f db` to monitor progress.

PostgreSQL is also exposed on **port 5433** (to avoid conflicts with a locally installed Postgres instance):

```bash
psql -h localhost -p 5433 -U project_user -d comp3161-group_project
```

### Test Accounts

Three ready-to-use accounts are seeded automatically:

| UserID | Password | Role |
|---|---|---|
| `test_student` | `password123` | Student |
| `test_lecturer` | `password123` | Lecturer |
| `test_admin` | `password123` | Admin |

Use these with `POST /api/auth/login` or via the Login page.

### Re-generating Seed Data

```bash
# Requires Python + faker
pip install faker
python insertdata.py   # overwrites project_insert_data.sql

# Reload into a running container
docker exec -i comp3161-groupproject-db-1 \
  psql -U project_user -d comp3161-group_project < project_insert_data.sql
```

> **Note:** Bulk-seeded users' passwords are SHA-256 hashes and **cannot** log in via the API.
> Use the test accounts above or register a new account via `POST /api/auth/register`.

---

## API Reference

### Auth
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | — | Create account |
| POST | `/api/auth/login` | — | Get JWT token |

### Courses
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses` | public | All courses |
| GET | `/api/courses/<id>` | JWT | Course detail |
| POST | `/api/courses` | Admin | Create course |
| GET | `/api/students/<id>/courses` | JWT | Student's courses |
| GET | `/api/lecturers/<id>/courses` | JWT | Lecturer's courses |
| POST | `/api/courses/<id>/enroll` | Student/Admin | Enrol in course |
| POST | `/api/courses/<id>/assign-lecturer` | Admin | Assign lecturer |
| GET | `/api/courses/<id>/members` | JWT | Course roster |

### Calendar
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses/<id>/events` | JWT | All events for course |
| POST | `/api/courses/<id>/events` | Lecturer/Admin | Create event |
| GET | `/api/students/<id>/events?date=YYYY-MM-DD` | JWT | Events on a date |

### Forums & Threads
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses/<id>/forums` | JWT | All forums |
| POST | `/api/courses/<id>/forums` | Lecturer/Admin | Create forum |
| GET | `/api/forums/<id>/threads` | JWT | Forum threads |
| POST | `/api/forums/<id>/threads` | JWT | Post thread |
| GET | `/api/threads/<id>` | JWT | Thread + reply tree |
| POST | `/api/threads/<id>/replies` | JWT | Reply to thread |
| POST | `/api/replies/<id>/replies` | JWT | Nested reply |

### Course Content
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses/<id>/content` | JWT | Sections + items |
| POST | `/api/courses/<id>/sections` | Lecturer/Admin | Add section |
| POST | `/api/sections/<id>/content` | Lecturer/Admin | Add content item |

### Assignments & Grades
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses/<id>/assignments` | JWT | List assignments |
| POST | `/api/courses/<id>/assignments` | Lecturer/Admin | Create assignment |
| POST | `/api/assignments/<id>/submit` | Student | Submit work |
| GET | `/api/assignments/<id>/submissions` | JWT | View submissions |
| POST | `/api/submissions/<id>/grade` | Lecturer/Admin | Grade submission |
| GET | `/api/students/<id>/average` | JWT | Overall GPA |

### Reports (views)
| Endpoint | Description |
|---|---|
| `GET /api/reports/courses-50plus` | Courses with ≥ 50 students |
| `GET /api/reports/students-5plus` | Students in ≥ 5 courses |
| `GET /api/reports/lecturers-3plus` | Lecturers teaching ≥ 3 courses |
| `GET /api/reports/top10-enrolled` | 10 most enrolled courses |
| `GET /api/reports/top10-averages` | Top 10 students by average |

---

## Local Development (without Docker)

```bash
# Backend — requires a locally running PostgreSQL instance
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt

# Set DATABASE_URL in .env to point at your local Postgres, e.g.:
# DATABASE_URL=postgresql://project_user:password@localhost:5432/comp3161-group_project
flask --app app:create_app run --debug

# Frontend
cd frontend
npm install
npm run dev                   # Vite dev server at http://localhost:5173
```

---

## Deployment (VPS)

```bash
# On a server with Docker + Docker Compose installed:
git clone <repo-url>
cd comp3161-groupproject
cp .env.example .env
# Fill in POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, and JWT_SECRET_KEY
docker compose up -d --build
```

Add your domain to `nginx/nginx.conf`'s `server_name` directive and set up SSL with Certbot.

---

## CI/CD

GitHub Actions runs on every push/PR to `main` or `develop`:

1. **Lint Python** — flake8 (syntax + style)
2. **TypeScript type-check + Vite build**
3. **Docker Compose build verification** (requires lint + build to pass)
4. **Push images to Docker Hub** — on merge to `main` only (requires `DOCKERHUB_USERNAME` + `DOCKERHUB_TOKEN` repository secrets)
