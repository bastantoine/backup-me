import typing as t
from enum import Enum

from .base import BaseSource
from .db import MySQLDB, PostgresDB
from .files import ArchiveType, RawFiles
from .http import HTTP


class SourceTypes(str, Enum):
    mysql = "mysql"
    postgres = "postgres"
    files = "files"
    http = "http"


SOURCES: t.Dict[SourceTypes, BaseSource] = {
    SourceTypes.mysql: MySQLDB,
    SourceTypes.postgres: PostgresDB,
    SourceTypes.files: RawFiles,
    SourceTypes.http: HTTP,
}

__all__ = [
    "BaseSource",
    "SOURCES",
    "ArchiveType",
    "RawFiles",
    "MySQLDB",
    "PostgresDB",
    "HTTP",
]
