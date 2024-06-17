import pytest
from pydantic import ValidationError

from backup_me.config import Config
from backup_me.destinations import S3
from backup_me.sources import DBSource, RawFiles


def test_invalid_source_type():
    raw_config = {
        "app": "my-app",
        "sources": [{"type": "invalid_source"}],
    }
    with pytest.raises(ValueError, match="Invalid source type") as err:
        Config(config=raw_config)


def test_invalid_destination_type():
    raw_config = {
        "app": "my-app",
        "sources": [],
        "destinations": [{"type": "invalid_destination"}],
    }
    with pytest.raises(ValueError, match="Invalid destination type") as err:
        Config(config=raw_config)


def test_valid_config():
    raw_config = {
        "app": "my-app",
        "sources": [
            {
                "type": "files",
                "backup_filename": "config",
                "files": ["file1", "file2"],
            },
        ],
        "destinations": [
            {
                "type": "s3",
                "name": "contabo",
                "bucket": "my-bucket.tests-backups",
                "access_key_id": "access_key_id",
                "secret_access_key": "secret_access_key",
                "prefix": "my-app",
            }
        ],
    }
    config = Config(config=raw_config)
    assert config.app == "my-app"

    assert len(config.sources) == 1
    files_src = RawFiles(
        backup_filename="config",
        files=["file1", "file2"],
    )
    assert config.sources[0] == files_src

    assert len(config.destinations) == 1
    s3_dest = S3(
        name="contabo",
        bucket="my-bucket.tests-backups",
        access_key_id="access_key_id",
        secret_access_key="secret_access_key",
        prefix="my-app",
    )
    assert config.destinations[0] == s3_dest


def test_dbsource_validation():
    with pytest.raises(ValidationError) as err:
        DBSource(
            host="localhost",
            port=5432,
            username="",
            password="",
            backup_filename="",
        )
        assert (
            err.value.errors()[0]["msg"]
            == "Value error, missing either database name or all_databases option"
        )
