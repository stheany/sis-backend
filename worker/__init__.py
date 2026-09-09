from celery import Celery
import os

celery_app = Celery(
    "sis",
    broker=os.environ.get("CELERY_BROKER_URL", "amqp://admin:mypass@rabbit:5672/"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "rpc://"),
)

# Optional Celery configuration
celery_app.conf.update(
    timezone=os.environ.get("TZ", "Asia/Phnom_Penh"),
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Force import of task modules - this ensures tasks are registered
import worker.pm_book_tasks
import worker.tasks  # if this file exists
import worker.bklv_tasks

# Optional: verify tasks are registered
print("Registered tasks:", list(celery_app.tasks.keys()))