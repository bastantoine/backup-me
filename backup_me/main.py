import json

import typer

from backup_me.backup import Backup
from backup_me.config import Config


def main(config_file: str):
    with open(config_file) as f:
        config = Config(json.load(f))

    backup = Backup(config)
    backup.run()


if __name__ == "__main__":
    typer.run(main)
