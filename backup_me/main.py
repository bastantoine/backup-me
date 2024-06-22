import typer

from backup_me.backup import Backup


def main(config_file: str):
    backup = Backup(config_file=config_file)
    backup.run()


def console():
    typer.run(main)


if __name__ == "__main__":
    typer.run(main)
