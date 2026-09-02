import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    "prism_collection_engine",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["collectors.mock_forum"]
)

app.conf.update(
    result_expires=3600,
    timezone='UTC',
)

if __name__ == '__main__':
    app.start()
