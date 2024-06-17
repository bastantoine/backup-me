import json

from backup_me.backup import Backup
from backup_me.config import Config


def main():
    with open("./config.json") as f:
        config = Config(json.load(f))

    backup = Backup(config)
    backup.run()


if __name__ == "__main__":
    main()
