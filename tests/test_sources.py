import os
import tarfile
import zipfile
from datetime import datetime

from backup_me.sources import ArchiveType, MySQLDB, PostgresDB, RawFiles


def test_rawfiles_source(tmp_path):
    with open(tmp_path / "file1.txt", "w") as f:
        f.write("content")
        f.flush()
    with open(tmp_path / "file2.txt", "w") as f:
        f.write("content")
        f.flush()

    # No archive_type provided => default to tar
    files_src = RawFiles(
        backup_filename="backup",
        files=[
            str(tmp_path / "file1.txt"),
            str(tmp_path / "file2.txt"),
        ],
    )
    backup = files_src.backup(tmp_path)
    assert backup.endswith(".tar")
    with tarfile.TarFile(backup) as archive:
        content = [os.path.basename(filename) for filename in archive.getnames()]
        assert len(content) == len(files_src.files)
        for file in files_src.files:
            assert os.path.basename(file) in content

    # Try with zip archive
    files_src = RawFiles(
        backup_filename="backup",
        files=[
            str(tmp_path / "file1.txt"),
            str(tmp_path / "file2.txt"),
        ],
        archive_type=ArchiveType.zip,
    )
    backup = files_src.backup(tmp_path)
    assert backup.endswith(".zip")
    with zipfile.ZipFile(backup) as archive:
        content = [os.path.basename(filename) for filename in archive.namelist()]
        assert len(content) == len(files_src.files)
        for file in files_src.files:
            assert os.path.basename(file) in content


def test_mysql_source(tmp_path, fake_process, mocker):
    now = datetime.now()
    mock_date = mocker.patch("backup_me.sources.datetime")
    mock_date.now.return_value = now

    backup_filename = "backup"
    args = {
        "backup_filename": backup_filename,
        "name": "db",
        "host": "localhost",
        "username": "username",
        "password": "password",
    }
    mysql_source = MySQLDB(database="db", **args)
    filename = f"{os.path.join(tmp_path, backup_filename)}_{mysql_source.now()}.sql"
    cmd = f"mysqldump --host={args['host']} --port=3306 --user={args['username']} --password={args['password']} db > {filename}"
    fake_process.register(cmd, stdout="")
    backup = mysql_source.backup(tmp_path)
    assert backup == filename
    assert fake_process.call_count(cmd) == 1

    mysql_source = MySQLDB(all_databases=True, **args)
    cmd = f"mysqldump --host={args['host']} --port=3306 --user={args['username']} --password={args['password']} --all-databases > {filename}"
    fake_process.register(cmd, stdout="")
    backup = mysql_source.backup(tmp_path)
    assert backup == filename
    assert fake_process.call_count(cmd) == 1

    os.environ["MYSQL_DB_USERNAME"] = args.pop("username")
    os.environ["MYSQL_DB_PASSWORD"] = args.pop("password")
    mysql_source = MySQLDB(all_databases=True, **args)
    fake_process.register(cmd, stdout="")
    backup = mysql_source.backup(tmp_path)
    assert fake_process.call_count(cmd) == 2


def test_postgres_source(tmp_path, fake_process, mocker):
    now = datetime.now()
    mock_date = mocker.patch("backup_me.sources.datetime")
    mock_date.now.return_value = now

    backup_filename = "backup"
    args = {
        "backup_filename": backup_filename,
        "name": "db",
        "host": "localhost",
        "username": "username",
        "password": "password",
    }
    postgres_source = PostgresDB(database="db", **args)
    filename = f"{os.path.join(tmp_path, backup_filename)}_{postgres_source.now()}.sql"
    cmd = f"pg_dump --host=localhost --port=5432 --username=username db > {filename}"
    fake_process.register(cmd, stdout="")
    backup = postgres_source.backup(tmp_path)
    assert backup == filename
    assert fake_process.call_count(cmd) == 1

    postgres_source = PostgresDB(all_databases=True, **args)
    filename = f"{os.path.join(tmp_path, backup_filename)}_{postgres_source.now()}.sql"
    cmd = f"pg_dumpall --host=localhost --port=5432 --username=username  > {filename}"
    fake_process.register(cmd, stdout="")
    backup = postgres_source.backup(tmp_path)
    assert backup == filename
    assert fake_process.call_count(cmd) == 1

    os.environ["PG_DB_USERNAME"] = args.pop("username")
    os.environ["PG_DB_PASSWORD"] = args.pop("password")
    postgres_source = PostgresDB(all_databases=True, **args)
    fake_process.register(cmd, stdout="")
    backup = postgres_source.backup(tmp_path)
    assert fake_process.call_count(cmd) == 2
