import json
import os
import typing as t

import requests

from .base import BaseSource


class HTTP(BaseSource):
    url: str
    method: str
    request_params: t.Dict[str, t.Any]

    def backup(self, output_dir: str) -> str:
        resp = requests.request(self.method, self.url, **self.request_params)

        result = {
            "url": self.url,
            "timestamp": self.now(),
            "result": resp.status_code,
        }
        is_json = resp.headers.get("Content-Type", "").lower() == "application/json"
        if is_json:
            result["detail"] = resp.json()
        else:
            result["msg"] = resp.text

        backup_filename = (
            f"{os.path.join(output_dir, self.backup_filename)}_{self.now()}.json"
        )
        with open(backup_filename, "w") as f:
            json.dump(result, f)

        if resp.ok:
            print(f"HTTP call for backup completed successfully.")
        else:
            print(
                f"HTTP call for backup failed with return code {resp.status_code} {resp.text}."
            )

        return backup_filename
