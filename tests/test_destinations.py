from pathlib import Path

from moto import mock_aws

from backup_me.destinations import S3


@mock_aws
def test_s3_destination(tmp_path: Path):
    file = tmp_path / "test.tar.gz"
    with open(file, "w") as f:
        f.write("")
        f.flush()
    s3_dest = S3(
        name="src",
        bucket="XXXXXXXXXXX",
        prefix="test",
        access_key_id="XXXXXXXXXXXXX",
        secret_access_key="XXXXXXXXXXXXX",
    )
    # Try to upload the file, any exception would mean an error in the upload process.
    s3_dest.upload([file.absolute()])
