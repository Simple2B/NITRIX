import subprocess
from celery import Celery

from config import BaseConfig as conf


celery = Celery(__name__)
celery.conf.broker_url = conf.REDIS_URL_FOR_CELERY


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        conf.CELERY_PERIODIC_CHECK_TIME,
        ninja_sync.s(),
        name="sync",
    )


@celery.task
def ninja_sync():
    flask_proc = subprocess.Popen(["flask", "scheduler-task"])
    flask_proc.communicate()
