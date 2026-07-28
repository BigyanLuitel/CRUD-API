from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

tasks = [
    {"id":1, "title" : "Open Shop","done":True},
    {"id":2, "title" : "Buy Groceries","done":False},
    {"id":3, "title" : "Clean Shop","done":False}
]
class TaskCreate(BaseModel):
    title: str = ""

@app.get("/")
def get_root():
    return {"name":"Task API","version":"1.0","endpoints":["/tasks"]}

@app.get("/health")
def get_health():
    return {"status" : "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks")
def create_task(task: TaskCreate):
    if not task.title:
        raise HTTPException(status_code=400, detail="Title is required")
    
    next_id = max(task["id"] for task in tasks) + 1 if tasks else 1
    new_task = {"id": next_id, "title": task.title, "done": "False"}
    tasks.append(new_task)
    raise HTTPException(status_code=201, detail="Task created successfully")
