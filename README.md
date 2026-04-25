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
│   ├── schema.sql        CREATE TABLE statements (12 tables)
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
├── docker-compose.yml
└── .github/workflows/ci.yml
```

---

## Quick Start (Docker)

```bash
# 1. Clone the repo
git clone <repo-url>
cd comp3161-project

# 2. Configure environment
cp .env.example .env
# Edit .env and set a strong JWT_SECRET_KEY

# 3. Start all services (DB, backend, frontend)
docker compose up --build

# 4. Open http://localhost in your browser
```

PostgreSQL is also exposed on port 5432 for local DBA access.

### Seeding the Database

After the containers are up, load the generated SQL dump (or re-generate it):

```bash
# Option A: use the pre-generated file
docker exec -i comp3161-project-db-1 \
  psql -U courseuser -d coursedb < project_insert_data.sql

# Option B: regenerate (requires Python + faker)
pip install faker
python insertdata.py
docker exec -i comp3161-project-db-1 \
  psql -U courseuser -d coursedb < project_insert_data.sql
```

> **Note:** Seeded users' passwords are SHA-256 hashes of `{FirstName}{LastName}{index}`.
> They cannot log in via the normal API login flow. Create a fresh account via
> `POST /api/auth/register` for API testing.

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
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
# Set DATABASE_URL in .env pointing to your local Postgres
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
cd comp3161-project
cp .env.example .env          # set JWT_SECRET_KEY to a long random value
docker compose up -d --build
```

Add your domain to the nginx `server_name` directive and set up SSL with Certbot.

## CI/CD

GitHub Actions runs on every push/PR to `main` or `develop`:
1. Python flake8 lint
2. TypeScript type-check + Vite build
3. Docker Compose build verification
4. On merge to `main`: push images to Docker Hub (requires `DOCKERHUB_USERNAME` + `DOCKERHUB_TOKEN` secrets)
