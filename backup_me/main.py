import typer

from backup_me.backup import Backup


def main(config_file: str):
    backup = Backup(config_file=config_file)
    backup.run()


if __name__ == "__main__":
    typer.run(main)
