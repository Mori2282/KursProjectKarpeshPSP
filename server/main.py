import json
import uuid
import shutil
from pathlib import Path
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import settings
from database.connection import get_db, engine, Base
from database.models import Task, TaskStatus
from server.schemas import TaskResponse, BatchUploadResponse
from workers.tasks import process_image_task

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/tasks/upload", response_model=BatchUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_batch(
    pipeline_config: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    try:
        steps = json.loads(pipeline_config)
        if not isinstance(steps, list):
            raise ValueError
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON array in pipeline_config")

    created = []
    for file in files:
        task_id = str(uuid.uuid4())
        ext = Path(file.filename).suffix or ".jpg"
        target_path = settings.UPLOAD_DIR / f"{task_id}{ext}"

        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        db_task = Task(
            id=task_id,
            status=TaskStatus.PENDING,
            original_filename=file.filename,
            input_path=str(target_path),
            pipeline_config=steps
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        process_image_task.delay(task_id)
        created.append(db_task)

    return {"enqueued_tasks": created}

@app.get("/tasks", response_model=List[TaskResponse])
def get_all_tasks(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.created_at.desc()).limit(limit).all()

@app.get("/tasks/{task_id}/download")
def download_result(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != TaskStatus.COMPLETED or not task.output_path:
        raise HTTPException(status_code=400, detail="Task not ready or failed")

    return FileResponse(path=task.output_path, media_type="image/png", filename=f"proc_{task.original_filename}")
