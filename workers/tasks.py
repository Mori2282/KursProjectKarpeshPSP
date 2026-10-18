from datetime import datetime
from config import settings
from database.connection import SessionLocal
from database.models import Task, TaskStatus
from pipelines.executor import PipelineExecutor
from workers.celery_app import celery_app

@celery_app.task(bind=True, name="process_image_task")
def process_image_task(self, task_id: str):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        db.close()
        return {"error": "Task not found"}

    try:
        task.status = TaskStatus.PROCESSING
        db.commit()

        output_filename = f"processed_{task.id}.png"
        output_path = str(settings.RESULT_DIR / output_filename)

        PipelineExecutor.process(
            input_path=task.input_path,
            output_path=output_path,
            steps=task.pipeline_config
        )

        task.output_path = output_path
        task.status = TaskStatus.COMPLETED
        task.updated_at = datetime.utcnow()
        db.commit()
        return {"status": "success", "output_path": output_path}

    except Exception as exc:
        db.rollback()
        task.status = TaskStatus.FAILED
        task.error_message = str(exc)
        task.updated_at = datetime.utcnow()
        db.commit()
        raise exc
    finally:
        db.close()
