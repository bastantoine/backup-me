import tempfile

from backup_me.config import Config
from backup_me.sources import ArchiveType, RawFiles


class Backup:
    config: Config

    def __init__(self, config: Config = None, config_file: str = None) -> None:
        if not config and not config_file:
            raise ValueError("Either config or config_file must be provided")
        if config_file and not config:
            config = Config.from_file(config_file)
        self.config = config

    def run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_files = []
            for src in self.config.sources:
                res = src.backup(output_dir=temp_dir)
                backup_files.append(res)

            raw_files_src = RawFiles(
                backup_filename=f"{self.config.app}_backup",
                archive_type=ArchiveType.tar.value,
                files=backup_files,
            )
            archived_files = raw_files_src.backup(temp_dir)

            for dest in self.config.destinations:
                if dest.group:
                    dest.upload([archived_files])
                else:
                    dest.upload(backup_files)
