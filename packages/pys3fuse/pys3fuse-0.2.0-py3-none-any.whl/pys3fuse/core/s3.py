from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import aioboto3
from boto3_type_annotations.s3 import Client

from .config import settings

session = aioboto3.Session(
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)


@asynccontextmanager
async def get_s3_client() -> AsyncGenerator[Client, Any]:
    client: Client = session.client("s3", endpoint_url=settings.S3_API)
    try:
        yield client
    finally:
        await client.close()
