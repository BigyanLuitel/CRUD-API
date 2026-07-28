from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="Task API",
    version="1.0",
    description="Simple in-memory To-Do List API"
)

# In-memory storage
tasks = []


# Request Models
class TaskCreate(BaseModel):
    title: str = Field(..., description="Task title")


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# Root Endpoint
@app.get("/", summary="Get API information")
def root():
    """Returns basic API information."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


# Health Check
@app.get("/health", summary="Check API health")
def health():
    """Returns API health status."""
    return {"status": "ok"}


# Get All Tasks
@app.get("/tasks", summary="Get all tasks")
def get_tasks():
    """Returns the full list of tasks."""
    return tasks


# Get One Task
@app.get("/tasks/{task_id}", summary="Get a task by ID")
def get_task(task_id: int):
    """Returns a single task."""
    task = next((t for t in tasks if t["id"] == task_id), None)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


# Create Task
@app.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
def create_task(task: TaskCreate):
    """Creates a new task."""
    if not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    next_id = max((t["id"] for t in tasks), default=0) + 1

    new_task = {
        "id": next_id,
        "title": task.title.strip(),
        "done": False
    }

    tasks.append(new_task)
    return new_task


# Partial Update Task
@app.put("/tasks/{task_id}", summary="Update an existing task")
def update_task(task_id: int, updates: TaskUpdate):
    """Updates provided fields of a task."""
    task = next((t for t in tasks if t["id"] == task_id), None)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if updates.title is not None:
        if not updates.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty"
            )
        task["title"] = updates.title.strip()

    if updates.done is not None:
        task["done"] = updates.done

    return task


# Delete Task
@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task"
)
def delete_task(task_id: int):
    """Deletes a task."""
    index = next(
        (i for i, t in enumerate(tasks) if t["id"] == task_id),
        None
    )

    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    tasks.pop(index)

    return Response(status_code=status.HTTP_204_NO_CONTENT)