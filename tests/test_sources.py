import json
import os
import tarfile
import zipfile
from datetime import datetime

import pytest

from backup_me.sources import HTTP, ArchiveType, MySQLDB, PostgresDB, RawFiles


def test_rawfiles_source(tmp_path):
    with open(tmp_path / "file1.txt", "w") as f:
        f.write("content")
        f.flush()
    with open(tmp_path / "file2.txt", "w") as f:
        f.write("content")
        f.flush()

    args = {
        "backup_filename": "backup",
        "name": "files_src",
        "files": [
            str(tmp_path / "file1.txt"),
            str(tmp_path / "file2.txt"),
        ],
    }
    # No archive_type provided => default to tar
    files_src = RawFiles(**args)
    backup = files_src.backup(tmp_path)
    assert backup.endswith(".tar")
    with tarfile.TarFile(backup) as archive:
        content = [os.path.basename(filename) for filename in archive.getnames()]
        assert len(content) == len(files_src.files)
        for file in files_src.files:
            assert os.path.basename(file) in content

    # Try with zip archive
    files_src = RawFiles(**args, archive_type=ArchiveType.zip)
    backup = files_src.backup(tmp_path)
    assert backup.endswith(".zip")
    with zipfile.ZipFile(backup) as archive:
        content = [os.path.basename(filename) for filename in archive.namelist()]
        assert len(content) == len(files_src.files)
        for file in files_src.files:
            assert os.path.basename(file) in content


def test_mysql_source(tmp_path, fake_process, mocker):
    now = datetime.now()
    mock_date = mocker.patch("backup_me.sources.base.datetime")
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
    mock_date = mocker.patch("backup_me.sources.base.datetime")
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


@pytest.mark.parametrize(
    "status,json_body,text_body",
    [
        (200, {"status": "OK", "msg": "Success"}, ""),
        (200, {}, "Sucess"),
        (500, {"status": "KO", "msg": "Error"}, ""),
        (500, {}, "Error"),
    ],
)
def test_http_source(status, json_body, text_body, tmp_path, requests_mock, mocker):
    now = datetime.now()
    mock_date = mocker.patch("backup_me.sources.base.datetime")
    mock_date.now.return_value = now

    url = "https://backup.me"
    args = {"status_code": status}
    if json_body:
        args["json"] = json_body
        args["headers"] = {"Content-Type": "application/json"}
    else:
        args["text"] = text_body
    requests_mock.post(url, **args)

    backup_filename = "backup"
    source = HTTP(
        backup_filename=backup_filename,
        name="http",
        url=url,
        method="POST",
        request_params={"headers": {"Authorization": "Bearer XYZ"}},
    )
    filename = f"{os.path.join(tmp_path, backup_filename)}_{source.now()}.json"
    backup = source.backup(tmp_path)
    assert backup == filename
    with open(backup) as f:
        result = json.load(f)
    expected = {
        "url": url,
        "timestamp": source.now(),
        "result": status,
    }
    if json_body:
        expected["detail"] = json_body
    else:
        expected["msg"] = text_body

    assert result == expected
