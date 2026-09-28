"""boto3 templates hardened for VAST Data S3."""

from .client import get_s3_client, get_s3_resource, get_transfer_config
from .config import Settings, load_settings

__all__ = [
    "Settings",
    "load_settings",
    "get_s3_client",
    "get_s3_resource",
    "get_transfer_config",
]
