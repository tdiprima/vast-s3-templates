"""Tiny shared helpers for the scripts/ CLIs."""

from __future__ import annotations

import argparse

from .client import get_s3_client
from .config import load_settings


def parser(description: str, bucket: bool = True) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    if bucket:
        p.add_argument("-b", "--bucket", help="bucket (default: $VAST_S3_BUCKET)")
    return p


def resolve(args) -> tuple:
    """Return (s3_client, bucket) with bucket falling back to VAST_S3_BUCKET."""
    settings = load_settings()
    s3 = get_s3_client(settings)
    bucket = getattr(args, "bucket", None) or settings.default_bucket
    if bucket is None and hasattr(args, "bucket"):
        raise SystemExit("error: pass --bucket or set VAST_S3_BUCKET")
    return s3, bucket


def fmt_size(n: int) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PiB"
