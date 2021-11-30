import os
import time
import subprocess
from datetime import datetime
from config import BaseConfig as conf
from app.logger import log

DB_DUMP_DIR = os.environ.get("DB_DUMP_DIR_CONT")
DB_DUMP_DAYS_PERIOD = conf.DB_DUMP_DAYS_PERIOD
SECONDS_IN_ONE_DAY = 86400
DB_DUMP_DAYS_IN_SECONDS = DB_DUMP_DAYS_PERIOD * SECONDS_IN_ONE_DAY


def get_filename() -> str:
    return datetime.today().strftime("%Y-%m-%d-%H-%M-%S") + ".sql"


def remove_old_data():
    now = time.time()
    for f in os.listdir(DB_DUMP_DIR):
        f = os.path.join(DB_DUMP_DIR, f)
        if os.path.isfile(f) and f.endswith(".sql"):
            log(log.INFO, "Find file :[%s]", f)
            if os.stat(f).st_mtime < now - DB_DUMP_DAYS_IN_SECONDS:
                os.remove(f)
                log(log.INFO, "File removed :[%s]", f)


def db_dumper():
    db_url = conf.DATABASE_URL
    cmd = ["pg_dump", db_url]
    filename = get_filename()
    file_path = os.path.join(DB_DUMP_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        subprocess.run(cmd, stdout=f)
    log(log.INFO, "CREATED dump file :[%s]", filename)
    remove_old_data()
