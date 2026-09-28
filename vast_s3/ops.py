"""Reusable helpers wrapping the common S3 operations."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

from botocore.exceptions import ClientError

from .client import get_transfer_config


def bucket_exists(s3, bucket: str) -> bool:
    try:
        s3.head_bucket(Bucket=bucket)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] in {"404", "NoSuchBucket"}:
            return False
        raise


def create_bucket(s3, bucket: str) -> bool:
    """Create a bucket; return False if it already existed."""
    if bucket_exists(s3, bucket):
        return False
    # No CreateBucketConfiguration: VAST rejects LocationConstraint.
    s3.create_bucket(Bucket=bucket)
    return True


def upload_file(s3, path: str | os.PathLike, bucket: str, key: str | None = None,
                content_type: str | None = None, metadata: dict | None = None) -> str:
    path = Path(path)
    key = key or path.name
    extra: dict = {}
    if content_type:
        extra["ContentType"] = content_type
    if metadata:
        extra["Metadata"] = metadata
    s3.upload_file(str(path), bucket, key, ExtraArgs=extra or None,
                   Config=get_transfer_config())
    return key


def upload_bytes(s3, data: bytes, bucket: str, key: str,
                 content_type: str = "application/octet-stream") -> None:
    s3.put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)


def download_file(s3, bucket: str, key: str, dest: str | os.PathLike) -> Path:
    dest = Path(dest)
    if dest.is_dir():
        dest = dest / Path(key).name
    dest.parent.mkdir(parents=True, exist_ok=True)
    s3.download_file(bucket, key, str(dest), Config=get_transfer_config())
    return dest


def read_bytes(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def list_objects(s3, bucket: str, prefix: str = "") -> Iterator[dict]:
    """Yield every object under ``prefix`` (handles pagination)."""
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        yield from page.get("Contents", [])


def delete_object(s3, bucket: str, key: str, version_id: str | None = None) -> None:
    kwargs = {"Bucket": bucket, "Key": key}
    if version_id:
        kwargs["VersionId"] = version_id
    s3.delete_object(**kwargs)


def delete_prefix(s3, bucket: str, prefix: str) -> int:
    """Delete all objects under ``prefix`` in batches of 1000. Returns count."""
    deleted = 0
    batch: list[dict] = []

    def flush():
        nonlocal deleted
        if batch:
            resp = s3.delete_objects(Bucket=bucket, Delete={"Objects": batch, "Quiet": True})
            errors = resp.get("Errors", [])
            if errors:
                raise RuntimeError(f"delete_objects errors: {errors[:3]}")
            deleted += len(batch)
            batch.clear()

    for obj in list_objects(s3, bucket, prefix):
        batch.append({"Key": obj["Key"]})
        if len(batch) == 1000:
            flush()
    flush()
    return deleted


def presigned_get_url(s3, bucket: str, key: str, expires: int = 3600) -> str:
    return s3.generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expires
    )


def presigned_put_url(s3, bucket: str, key: str, expires: int = 3600,
                      content_type: str | None = None) -> str:
    params = {"Bucket": bucket, "Key": key}
    if content_type:
        params["ContentType"] = content_type
    return s3.generate_presigned_url("put_object", Params=params, ExpiresIn=expires)


def set_versioning(s3, bucket: str, enabled: bool) -> None:
    s3.put_bucket_versioning(
        Bucket=bucket,
        VersioningConfiguration={"Status": "Enabled" if enabled else "Suspended"},
    )


def get_versioning(s3, bucket: str) -> str:
    return s3.get_bucket_versioning(Bucket=bucket).get("Status", "Disabled")


def list_versions(s3, bucket: str, prefix: str = "") -> Iterator[dict]:
    """Yield versions and delete markers, newest first per key."""
    paginator = s3.get_paginator("list_object_versions")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for v in page.get("Versions", []):
            yield {**v, "Kind": "version"}
        for d in page.get("DeleteMarkers", []):
            yield {**d, "Kind": "delete-marker"}
