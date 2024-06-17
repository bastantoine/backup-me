import tempfile

from backup_me.config import Config
from backup_me.sources import ArchiveType, RawFiles


class Backup:
    config: Config

    def __init__(self, config: Config) -> None:
        self.config = config

    def run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_files = []
            for src in self.config.sources:
                res = src.backup(temp_dir)
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
