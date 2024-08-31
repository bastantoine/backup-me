from datetime import datetime

from pydantic import BaseModel


class BaseSource(BaseModel):
    backup_filename: str
    name: str

    def backup(self, dir: str) -> str:
        raise NotImplementedError

    def now(self) -> str:
        return datetime.now().isoformat()
