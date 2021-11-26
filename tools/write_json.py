import os
from typing import Any
from pydantic import BaseModel
from app.logger import log


DB_MIGRATION_DIR = "data-migrations/"  # ninja dir?
os.makedirs(DB_MIGRATION_DIR, exist_ok=True)


class OutData(BaseModel):
    data: list[Any]


def write_json(file_name: str, data: OutData):
    file_path = os.path.join(DB_MIGRATION_DIR, f"{file_name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data.json(indent=2))
    log(log.DEBUG, "Created file: [%s]", file_path)
