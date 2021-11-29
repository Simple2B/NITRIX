import subprocess
from celery import Celery
from celery.schedules import crontab
from config import BaseConfig as conf
from app.dumper import db_dumper


celery = Celery(__name__)
celery.conf.broker_url = conf.REDIS_URL_FOR_CELERY


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        conf.CELERY_PERIODIC_CHECK_TIME,
        ninja_sync.s(),
        name="sync",
    )
    sender.add_periodic_task(crontab(minute=56, hour=23), pg_dumb.s(), name="pg_dumb")


@celery.task
def ninja_sync():
    flask_proc = subprocess.Popen(["flask", "scheduler-task"])
    flask_proc.communicate()


@celery.task
def pg_dumb():
    db_dumper()
