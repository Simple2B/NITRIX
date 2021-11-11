import time
from app.logger import log


def sync_scheduler():
    log(log.INFO, "[SHED] Start sync scheduler")
    time.sleep(5)
    log(log.INFO, "[SHED] Finished sync scheduler")
