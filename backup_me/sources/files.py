import os
import tarfile
import typing as t
import zipfile
from enum import Enum

from .base import BaseSource


class ArchiveType(str, Enum):
    zip = "zip"
    tar = "tar"


class RawFiles(BaseSource):
    files: t.List[str]
    archive_type: ArchiveType = ArchiveType.tar

    def backup(self, dir: str) -> str:
        backup_filename = f"{os.path.join(dir, self.backup_filename)}_{self.now()}.{self.archive_type.value}"

        # We can't use the shutil.make_archive function here, as this allows to archive only whole
        # folder, and not single files. We could copy all the files in a temp folder and then
        # archive this folder, but that my be a bit overkill.

        if self.archive_type == ArchiveType.tar:
            mode = "w"
            with tarfile.TarFile(backup_filename, mode) as archive:
                for file in self.files:
                    archive.add(os.path.expanduser(file))

        elif self.archive_type == ArchiveType.zip:
            with zipfile.ZipFile(backup_filename, "w") as archive:
                for file in self.files:
                    archive.write(os.path.expanduser(file))

        return backup_filename
