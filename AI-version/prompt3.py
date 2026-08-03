import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI()

DB_NAME = "tasks.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Learn FastAPI", 0),
                ("Build a REST API", 0),
                ("Connect to a database", 1),
            ]
        )
        conn.commit()
    conn.close()


init_db()


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/tasks")
def get_tasks(conn: sqlite3.Connection = Depends(get_db)):
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    return [dict(row) for row in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int, conn: sqlite3.Connection = Depends(get_db)):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(row)


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate, conn: sqlite3.Connection = Depends(get_db)):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    cursor = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, False)
    )
    conn.commit()
    new_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
    return dict(row)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, conn: sqlite3.Connection = Depends(get_db)):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    new_title = row["title"]
    new_done = row["done"]

    if task_update.title is not None:
        if not task_update.title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        new_title = task_update.title

    if task_update.done is not None:
        new_done = task_update.done

    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id)
    )
    conn.commit()
    updated_row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return dict(updated_row)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, conn: sqlite3.Connection = Depends(get_db)):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()