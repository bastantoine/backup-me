import os
import typing as t
from enum import Enum

import boto3
import botocore
from pydantic import BaseModel


class DestinationTypes(str, Enum):
    s3 = "s3"


class BaseDestination(BaseModel):
    group: bool = False
    name: str

    def upload(self, files: t.List[str]):
        raise NotImplementedError


class S3(BaseDestination):
    bucket: str
    access_key_id: str
    secret_access_key: str
    prefix: str = None
    endpoint_url: str = None
    region: str = "us-east-1"

    def __init__(self, **data):
        name = data.get("name").upper().replace(" ", "_")
        if not data.get("access_key_id"):
            data["access_key_id"] = os.getenv(f"S3_{name}_ACCESS_KEY_ID")
        if not data.get("secret_access_key"):
            data["secret_access_key"] = os.getenv(f"S3_{name}_SECRET_ACCESS_KEY")
        super().__init__(**data)

    def upload(self, files: t.List[str]):
        kwargs = {
            "aws_access_key_id": self.access_key_id,
            "aws_secret_access_key": self.secret_access_key,
            "region_name": self.region,
        }
        if self.endpoint_url:
            kwargs["endpoint_url"] = self.endpoint_url
        s3 = boto3.client("s3", **kwargs)

        try:
            s3.head_bucket(Bucket=self.bucket)
        except botocore.exceptions.ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                # Bucket doesn't exist, create it
                s3.create_bucket(Bucket=self.bucket)

        for filename in files:
            resp = s3.upload_file(
                Filename=filename,
                Bucket=self.bucket,
                Key=f"{self.prefix + '/' if self.prefix else ''}{os.path.basename(filename)}",
            )


DESTINATIONS = {
    DestinationTypes.s3: S3,
}
