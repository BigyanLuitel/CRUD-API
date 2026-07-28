from fastapi import FastAPI, HTTPException

app = FastAPI()

tasks = [
    {"id":1, "title" : "Open Shop","done":True},
    {"id":2, "title" : "Buy Groceries","done":False},
    {"id":3, "title" : "Clean Shop","done":False}
]

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