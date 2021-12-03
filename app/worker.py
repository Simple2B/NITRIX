import subprocess
from celery import Celery
from celery.schedules import crontab
from config import BaseConfig as conf
from app.dumper import db_dumper


CRON_MINUTE = 56
CRON_HOUR = 23

celery = Celery(__name__)
celery.conf.broker_url = conf.REDIS_URL_FOR_CELERY


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        conf.CELERY_PERIODIC_CHECK_TIME,
        ninja_sync.s(),
        name="sync",
    )
    sender.add_periodic_task(
        crontab(minute=CRON_MINUTE, hour=CRON_HOUR), pg_dump.s(), name="pg_dump"
    )


@celery.task
def ninja_sync():
    flask_proc = subprocess.Popen(["flask", "scheduler-task"])
    flask_proc.communicate()


@celery.task
def pg_dump():
    db_dumper()
