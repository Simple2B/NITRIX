import os
import json
from app.logger import log


DB_MIGRATION_DIR = "data-migrations/"


def read_json(file_name: str) -> list[dict]:
    file_path = os.path.join(DB_MIGRATION_DIR, f"{file_name}.json")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    log(log.DEBUG, "Read file: [%s]", file_path)
    return data["data"]
