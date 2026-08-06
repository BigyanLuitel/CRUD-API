# CRUD API

This is a small FastAPI project for managing a simple to-do list. It was built for the FlyRank AI Internship — Assignment A1 (Week 2) built the core CRUD API, and Assignment A2 (Week 3) connected it to a SQLite database, so tasks now persist across restarts.

The app keeps everything in memory, so there is no database involved. That makes it easy to run and test, but it also means the task list resets whenever the server restarts.

## What it does

- Create new tasks
- View all tasks
- View a single task by ID
- Update an existing task
- Delete a task
- Check the API health status

## How to run it

If you are using Windows, run the app with these steps:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn
uvicorn main:app --reload --port 8000
```

Once the server is running, open `http://localhost:8000` in your browser to confirm it is working. You can also visit `http://localhost:8000/docs` to try the API through Swagger UI.

## Endpoints

## | Method | Path | Purpose

| GET | `/` | Basic API info  
| GET | `/health` | Health check  
| GET | `/tasks` | Get all tasks  
| GET | `/tasks/{id}` | Get one task  
| POST | `/tasks` | Create a new task
| PUT | `/tasks/{id}` | Update a task  
| DELETE | `/tasks/{id}` | Remove a task

## Example

To add a task with `curl`, use:

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"
```

**Note:** The AI-generated code lives on a separate branch (`AI-version`), kept apart from the hand-built implementation on `main`.

## Screenshots

![API screenshot](image.png)
![Swagger UI screenshot](image-1.png)
![Task list screenshot](image-2.png)

## Database

This project uses **SQLite** for storage, via SQLAlchemy's ORM.

**Why SQLite:** no separate server to install or configure — the whole database is a single file. It's the natural next step from in-memory storage (Assignment 1) since it needs zero setup but still gives real persistence, which is exactly what this assignment is about.

**Where it lives:** `tasks.db`, created automatically the first time the app runs. It's git-ignored — each clone starts fresh with its own 3 seeded tasks rather than inheriting anyone else's data.

**Run it:**

```bash
python3 -m venv .venv
source .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install fastapi uvicorn sqlalchemy
uvicorn main:app --reload --port 8000
```

`tasks.db` and its `tasks` table are created automatically — no manual database setup needed.

**Exploring the database by hand:**

Opened `tasks.db` in [DB Browser for SQLite](https://sqlitebrowser.org/) and ran:

```sql
SELECT * FROM tasks WHERE done = 1;
```

This returned 1 row — only the seeded "Finish FlyRank assignment" task, before any updates. Running an `UPDATE` in DB Browser and then calling `GET /tasks` through the API immediately reflected the change with no restart needed, confirming the API and DB Browser read the exact same file.

## Running with Docker

This project runs as a two-container stack: the API and a PostgreSQL database, both managed by Docker Compose.

**Why Postgres + Docker:** SQLite (Assignment 2) works for a single file on one machine, but real backends run against a proper database server. Docker means Postgres runs identically on any machine — no manual install, no version conflicts, no "works on my machine."

**Setup:**

```bash
cp .env.example .env
docker compose up --build
```

That's it — one command builds the app image, starts Postgres, creates the `tasks` table, and seeds 3 example tasks on first run.

**Environment variables:** see `.env.example` for the required `DATABASE_URL` format.

**Example request:**

```bash
curl -i http://localhost:8000/tasks
```

**Persistence:** data survives a full stack restart — verified by creating a task, running `docker compose down` then `docker compose up`, and confirming the task is still there. This works because the database's data lives in a Docker **volume**, which outlives the containers themselves.

**Database screenshot:**
![Postgres data via psql](image1.png)

![Postgres data via psql](image.png)
