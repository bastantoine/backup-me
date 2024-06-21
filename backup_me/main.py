import typer

from backup_me.backup import Backup
from backup_me.config import Config


def main(config_file: str):
    config = Config.from_file(config_file)
    backup = Backup(config)
    backup.run()


if __name__ == "__main__":
    typer.run(main)
