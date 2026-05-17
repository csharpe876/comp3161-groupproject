# ETutor — Course Management System

This is our group project for COMP3161. ETutor is a full-stack e-learning platform where students can enrol in courses, submit assignments, participate in forums, and track their schedule — while lecturers and admins manage everything from a single dashboard.

## What we used

| Layer | Technology |
|---|---|
| Database | PostgreSQL 16 |
| Backend API | Python 3.12 · Flask 3 · psycopg2 (raw SQL, no ORM) |
| Auth | JWT (flask-jwt-extended) · bcrypt |
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS |
| Infrastructure | Docker · Docker Compose · Nginx |


---

## How the backend is structured

The backend follows an MVC pattern to keep things clean and testable:

- **Models** (`backend/models/`) — every database query lives here, one file per feature area
- **Controllers** (`backend/routes/`) — thin Flask blueprints that handle HTTP, call the model, and return JSON
- **Views** — just JSON via `flask.jsonify`

```
backend/
├── app.py               Application factory + blueprint registration
├── config.py            Environment-based config
├── db.py                psycopg2 connection pool + query helpers
├── models/              All SQL queries
│   ├── user.py
│   ├── course.py        Courses + enrollment
│   ├── assignment.py    Assignments, submissions, grades
│   ├── forum.py         Forums, threads, replies (recursive CTE for nesting)
│   ├── content.py       Course sections + content items
│   ├── calendar.py      Calendar events
│   └── report.py        Admin/lecturer report queries
└── routes/              HTTP handlers only — no SQL here
    ├── auth.py
    ├── courses.py
    ├── assignments.py
    ├── forums.py
    ├── content.py
    ├── calendar.py
    └── reports.py
```

---

## Project layout

```
├── backend/
├── database/
│   ├── schema.sql        All 11 CREATE TABLE statements
│   ├── views.sql         5 report views
│   └── indexes.sql       Performance indexes
├── frontend/             React SPA (Vite + TypeScript + Tailwind)
│   ├── nginx.conf        Nginx config (gzip, CSP headers, SPA fallback, API proxy)
│   └── src/
│       ├── pages/        Login, Register, Dashboard, CourseDetail,
│       │                 ForumDetail, ThreadDetail, AdminPanel
│       ├── components/   Layout, Navbar, ProtectedRoute, ReplyThread
│       ├── context/      AuthContext (JWT storage + refresh)
│       └── services/     Axios instance with JWT interceptor
├── nginx/nginx.conf      Alternative reverse proxy config for standalone deployments
├── docker-compose.yml
├── seed_data.py          Generates fresh seed data using Faker
├── project_insert_data.sql  Pre-generated seed data (auto-loaded on first start)
└── test_users.sql        Three ready-to-use test accounts (auto-loaded on first start)
```

---

## Getting started (Docker — easiest way)

The whole stack runs with a single command. You just need Docker installed.

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (comes with Docker Compose)

### Steps

```bash
# 1. Clone the repo
git clone <repo-url>
cd comp3161-groupproject

# 2. Set up your environment file
cp .env.example .env
```

Open `.env` and fill in your values. The defaults are fine for local dev, but please generate a real `JWT_SECRET_KEY` before sharing with anyone:

```env
POSTGRES_DB=comp3161-group_project
POSTGRES_USER=project_user
POSTGRES_PASSWORD=your-db-password

# "db" here is the Docker service name — don't change it unless you rename the service
DATABASE_URL=postgresql://project_user:your-db-password@db:5432/comp3161-group_project

# Generate one with: python -c "import secrets; print(secrets.token_hex(48))"
JWT_SECRET_KEY=change-me-to-a-long-random-secret

FLASK_ENV=production
```

```bash
# 3. Build and start everything
docker compose up -d --build

# 4. Open the app in your browser
start http://localhost        # Windows
open http://localhost         # macOS
```

### What happens behind the scenes on first start

Docker runs these SQL files against the database in order — you don't need to do anything manually:

| Order | File | What it does |
|---|---|---|
| 01 | `database/schema.sql` | Creates all 11 tables |
| 02 | `database/views.sql` | Creates the 5 report views |
| 03 | `database/indexes.sql` | Adds performance indexes |
| 04 | `test_users.sql` | Seeds the 3 test accounts |
| 05 | `project_insert_data.sql` | Loads the full dataset |

> The seed data takes a minute or two to load on first start. You can watch the progress with `docker compose logs -f db`.

### Handy commands

```bash
# Watch logs in real time
docker compose logs -f                      # all services
docker compose logs -f backend              # Flask API only

# Check that all containers are healthy
docker compose ps

# Shut everything down
docker compose down

# Full reset — wipes the database volume and starts fresh
docker compose down -v

# Rebuild after making code changes
docker compose up -d --build
```

### Connecting directly to PostgreSQL

We expose the database on port **5433** so it doesn't clash with any local Postgres you might have running:

```bash
psql -h localhost -p 5433 -U project_user -d comp3161-group_project
```

---

## Test accounts

These three accounts are loaded automatically and work on the Login page right away:

| Username | Password | Role |
|---|---|---|
| `test_student` | `password123` | Student |
| `test_lecturer` | `password123` | Lecturer |
| `test_admin` | `password123` | Admin |

> **Heads up:** The bulk-seeded users from `project_insert_data.sql` have SHA-256 hashed passwords (not bcrypt), so they can't log in through the API. Stick to the test accounts above, or just register a new one.

---

## Re-generating seed data

If you want a fresh dataset:

```bash
pip install faker
python seed_data.py   # overwrites project_insert_data.sql

# Load it into an already-running container
docker exec -i comp3161-groupproject-db-1 \
  psql -U project_user -d comp3161-group_project < project_insert_data.sql
```

---

## API Reference

All endpoints that say "JWT" require an `Authorization: Bearer <token>` header. You get the token from `POST /api/auth/login`.

### Auth
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | — | Create a new account |
| POST | `/api/auth/login` | — | Log in, returns a JWT token |
| GET | `/api/health` | — | Simple health check |

### Courses
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses` | — | List all courses |
| GET | `/api/courses/<id>` | JWT | Course details |
| POST | `/api/courses` | Admin | Create a course |
| GET | `/api/students/<id>/courses` | JWT | Courses a student is enrolled in |
| GET | `/api/lecturers/<id>/courses` | JWT | Courses a lecturer teaches |
| POST | `/api/courses/<id>/enroll` | Student/Admin | Enrol in a course |
| POST | `/api/courses/<id>/assign-lecturer` | Admin | Assign a lecturer to a course |
| GET | `/api/courses/<id>/members` | JWT | Everyone enrolled in a course |

### Calendar
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses/<id>/events` | JWT | All events for a course |
| POST | `/api/courses/<id>/events` | Lecturer/Admin | Create a calendar event |
| GET | `/api/students/<id>/events?date=YYYY-MM-DD` | JWT | A student's events on a specific date |

### Forums & Threads
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses/<id>/forums` | JWT | Forums in a course |
| POST | `/api/courses/<id>/forums` | Lecturer/Admin | Create a forum |
| GET | `/api/forums/<id>/threads` | JWT | Threads in a forum |
| POST | `/api/forums/<id>/threads` | JWT | Start a new thread |
| GET | `/api/threads/<id>` | JWT | Thread with the full nested reply tree |
| POST | `/api/threads/<id>/replies` | JWT | Reply to a thread |
| POST | `/api/replies/<id>/replies` | JWT | Reply to a reply |

### Course Content
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses/<id>/content` | JWT | All sections with their nested content items |
| POST | `/api/courses/<id>/sections` | Lecturer/Admin | Add a new section |
| POST | `/api/sections/<id>/content` | Lecturer/Admin | Add a content item to a section |

### Assignments & Grades
| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/courses/<id>/assignments` | JWT | List assignments for a course |
| POST | `/api/courses/<id>/assignments` | Lecturer/Admin | Create an assignment |
| POST | `/api/assignments/<id>/submit` | Student | Submit work |
| GET | `/api/assignments/<id>/submissions` | JWT | View all submissions |
| POST | `/api/submissions/<id>/grade` | Lecturer/Admin | Grade a submission |
| GET | `/api/students/<id>/average` | JWT | A student's overall grade average |

### Reports (Admin/Lecturer only)
| Endpoint | Description |
|---|---|
| `GET /api/reports/courses-50plus` | Courses with 50 or more enrolled students |
| `GET /api/reports/students-5plus` | Students enrolled in 5 or more courses |
| `GET /api/reports/lecturers-3plus` | Lecturers teaching 3 or more courses |
| `GET /api/reports/top10-enrolled` | The 10 most popular courses by enrolment |
| `GET /api/reports/top10-averages` | Top 10 students ranked by grade average |

---

## Running without Docker

If you'd rather run things locally during development:

### Backend

You'll need a PostgreSQL instance running locally first.

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt

# Update DATABASE_URL in .env to point at your local Postgres:
# DATABASE_URL=postgresql://project_user:password@localhost:5432/comp3161-group_project

flask --app app --debug run
```

### Frontend

```bash
cd frontend
npm install
npm run dev     # Starts Vite dev server at http://localhost:5173
```

> In dev mode, Vite automatically proxies `/api/*` to `http://localhost:5000`, so the frontend and backend work together without any extra config.

---

## Deploying to a server

```bash
# SSH into your server, then:
git clone <repo-url>
cd comp3161-groupproject
cp .env.example .env
# Set strong values for POSTGRES_PASSWORD and JWT_SECRET_KEY
docker compose up -d --build
```

The app runs on port **80** by default. To add HTTPS:

1. Point your domain's A record at the server's IP address.
2. Install Certbot: `snap install certbot --classic`
3. Get a certificate, add the `ssl_certificate` directives to `frontend/nginx.conf`, then `docker compose up -d --build`.
