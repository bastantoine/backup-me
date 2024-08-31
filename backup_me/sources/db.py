import os
import subprocess
import tempfile

from pydantic import model_validator

from .base import BaseSource


class DBSource(BaseSource):
    host: str
    port: int
    username: str
    password: str
    database: str = ""
    all_databases: bool = False

    @model_validator(mode="after")
    def check_db_name(self):
        if not self.database and not self.all_databases:
            raise ValueError("missing either database name or all_databases option")
        return self


class MySQLDB(DBSource):
    port: int = 3306
    mysql_dump_bin: str = "mysqldump"

    def __init__(self, **data):
        name = data.get("name").upper().replace(" ", "_")
        if not data.get("username"):
            data["username"] = os.getenv(f"MYSQL_{name}_USERNAME")
        if not data.get("password"):
            data["password"] = os.getenv(f"MYSQL_{name}_PASSWORD")
        super().__init__(**data)

    def backup(self, dir: str) -> str:
        if self.all_databases:
            database = "--all-databases"
        else:
            database = self.database

        backup_filename = f"{os.path.join(dir, self.backup_filename)}_{self.now()}.sql"
        command = f"{self.mysql_dump_bin} --host={self.host} --port={self.port} --user={self.username} --password={self.password} {database} > {backup_filename}"
        process = subprocess.run(command, shell=True)

        if process.returncode == 0:
            print(f"Database backup completed successfully: {backup_filename}.")
        else:
            print(f"Database backup failed with return code {process.returncode}.")

        return backup_filename


class PostgresDB(DBSource):
    port: int = 5432
    pg_dump_bin: str = "pg_dump"
    pg_dumpall_bin: str = "pg_dumpall"

    def __init__(self, **data):
        name = data.get("name").upper().replace(" ", "_")
        if not data.get("username"):
            data["username"] = os.getenv(f"PG_{name}_USERNAME")
        if not data.get("password"):
            data["password"] = os.getenv(f"PG_{name}_PASSWORD")
        super().__init__(**data)

    def backup(self, dir: str) -> str:
        if self.all_databases:
            bin = self.pg_dumpall_bin
            database_option = ""
            database_name = "*"
        else:
            bin = self.pg_dump_bin
            database_option = self.database
            database_name = database_option

        # Using the PGPASSFILE env var to provide the password to the CLI
        # https://www.postgresql.org/docs/current/libpq-pgpass.html
        # https://www.postgresql.org/docs/current/libpq-envars.html
        with tempfile.NamedTemporaryFile(mode="w") as temp_pgpassfile:
            temp_pgpassfile.write(
                f"{self.host}:{self.port}:{database_name}:{self.username}:{self.password}"
            )
            # We need to make sure the content has been written to the file before running the CLI
            temp_pgpassfile.flush()

            env = os.environ.copy()
            env["PGPASSFILE"] = temp_pgpassfile.name

            backup_filename = (
                f"{os.path.join(dir, self.backup_filename)}_{self.now()}.sql"
            )
            command = f"{bin} --host={self.host} --port={self.port} --username={self.username} {database_option} > {backup_filename}"
            process = subprocess.run(command, shell=True, env=env)

        if process.returncode == 0:
            print(f"Database backup completed successfully: {backup_filename}.")
        else:
            print(f"Database backup failed with return code {process.returncode}.")

        return backup_filename
