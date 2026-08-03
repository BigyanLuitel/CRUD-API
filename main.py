from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI()
DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    done = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_tasks(db: Session):
    if db.query(Task).count() == 0:
        initial_tasks = [
            Task(title="Task 1", done=False),
            Task(title="Task 2", done=True),
            Task(title="Task 3", done=False),
        ]
        db.add_all(initial_tasks)
        db.commit()

with SessionLocal() as db:
    seed_tasks(db)

class TaskCreate(BaseModel):
    title: str = ""

class TaskUpdate(BaseModel):
    title: Optional[str]= None
    done: Optional[bool]= None

@app.get("/")
def get_root():
    return {"name":"Task API","version":"1.0","endpoints":["/tasks"]}

@app.get("/health")
def get_health():
    return {"status" : "ok"}

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    if not task.title:
        raise HTTPException(status_code=400, detail="Title is required")
    
    new_task = Task(title=task.title, done=False)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    for existing_task in tasks:
        if existing_task["id"] == task_id:
            if task.title is not None:
                if not task.title.strip():
                    raise HTTPException(status_code=400, detail="Title cannot be empty")
                existing_task["title"] = task.title
            if task.done is not None:
                existing_task["done"] = task.done
            return existing_task
    
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            del tasks[index]
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")