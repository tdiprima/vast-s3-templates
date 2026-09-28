"""Environment-based configuration (reads .env if present)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


def _bool(value: str | None, default: bool) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    endpoint_url: str
    access_key: str
    secret_key: str
    region: str = "us-east-1"
    verify_ssl: bool | str = True
    default_bucket: str | None = None
    max_pool_connections: int = 32

    @property
    def mask(self) -> str:
        return f"{self.access_key[:4]}…  @ {self.endpoint_url}"


def load_settings(dotenv_path: str | None = None) -> Settings:
    """Load VAST_* variables from the environment (and .env)."""
    load_dotenv(dotenv_path, override=False)

    endpoint = os.getenv("VAST_S3_ENDPOINT")
    access = os.getenv("VAST_S3_ACCESS_KEY")
    secret = os.getenv("VAST_S3_SECRET_KEY")
    missing = [
        n
        for n, v in (
            ("VAST_S3_ENDPOINT", endpoint),
            ("VAST_S3_ACCESS_KEY", access),
            ("VAST_S3_SECRET_KEY", secret),
        )
        if not v
    ]
    if missing:
        raise RuntimeError(
            f"Missing required env vars: {', '.join(missing)} (see .env.example)"
        )

    # VAST_S3_CA_BUNDLE=/path/ca.pem takes precedence over VAST_S3_VERIFY_SSL.
    ca_bundle = os.getenv("VAST_S3_CA_BUNDLE")
    verify: bool | str = ca_bundle or _bool(os.getenv("VAST_S3_VERIFY_SSL"), True)

    return Settings(
        endpoint_url=endpoint.rstrip("/"),
        access_key=access,
        secret_key=secret,
        region=os.getenv("VAST_S3_REGION", "us-east-1"),
        verify_ssl=verify,
        default_bucket=os.getenv("VAST_S3_BUCKET") or None,
        max_pool_connections=int(os.getenv("VAST_S3_MAX_POOL_CONNECTIONS", "32")),
    )
