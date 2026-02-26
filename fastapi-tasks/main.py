from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from task_store import load_tasks, save_tasks, get_next_id, find_task_by_id

app = FastAPI(
    title="Task Management API",
    description="FastAPI backend for managing tasks (JSON Lines persistence)",
    version="1.0.0",
)


# REQUIREMENT: Pydantic models 
class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    completed: bool = False


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskUpdate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False


# REQUIREMENT: Endpoints

# NUM 1: GET /  Root check 
@app.get("/")
def root_check():
    return {"status": "healthy", "message": "API is running"}

# NUM 9: GET/ TASKS/ STATS Get task statistics 

# IMPORTATN INFO: DEFINE /tasks/stats BEFOREEE /tasks/{id}
@app.get("/tasks/stats")
def task_stats():
    tasks = load_tasks()
    total = len(tasks)
    completed_count = sum(1 for t in tasks if t.get("completed") is True)
    pending_count = total - completed_count

    if total == 0:
        completion_percentage = 0.0
    else:
        completion_percentage = (completed_count / total) * 100

    return {
        "total_tasks": total,
        "completed_tasks": completed_count,
        "pending_tasks": pending_count,
        "completion_percentage": completion_percentage,
    }


# NUM2 AND 7: Get all tasks (GET /tasks) with optional filter ?completed=true/false
@app.get("/tasks")
def get_all_tasks(completed: bool | None = None):
    tasks = load_tasks()
    if completed is None:
        return tasks
    return [t for t in tasks if t.get("completed") is completed]


# NUM 4: POST/TASKS Create task 
@app.post("/tasks")
def create_task(task: TaskCreate):
    tasks = load_tasks()
    new_id = get_next_id(tasks)

    new_task = {
        "id": new_id,
        "title": task.title,
        "description": task.description,
        "completed": False,  # default false
    }

    tasks.append(new_task)
    save_tasks(tasks)
    return new_task


# NUM 3: GET /tasks/{id} Get single task 
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    tasks = load_tasks()
    found = find_task_by_id(tasks, task_id)
    if not found:
        raise HTTPException(status_code=404, detail="Task Not Found")
    return found


# 05) Update Task (PUT /tasks/{id}) - complete replace of fields
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated: TaskUpdate):
    tasks = load_tasks()
    found = find_task_by_id(tasks, task_id)
    if not found:
        raise HTTPException(status_code=404, detail="Task Not Found")

    found["title"] = updated.title
    found["description"] = updated.description
    found["completed"] = updated.completed

    save_tasks(tasks)
    return found


# NUM 6: DELETE /tasks/{id} Delete task 
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    tasks = load_tasks()
    found = find_task_by_id(tasks, task_id)
    if not found:
        raise HTTPException(status_code=404, detail="Task Not Found")

    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    return {"message": "Task Deleted"}


# NUM 8: DELETE /tasks  Delete all tasks
@app.delete("/tasks")
def delete_all_tasks():
    save_tasks([])
    return {"message": "All Tasks Deleted"}