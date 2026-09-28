"""Hardened boto3 client factory for VAST Data S3.

Why this exists
---------------
boto3 >= 1.36 (Jan 2025) changed S3 defaults in ways that break many
S3-compatible backends, VAST included:

1. Default integrity checksums. boto3 now computes a CRC32 checksum for
   every PutObject/UploadPart and sends it as a *trailing* checksum using
   ``Content-Encoding: aws-chunked`` + ``x-amz-decoded-content-length``.
   Backends that don't understand aws-chunked store the chunk framing and
   trailer as part of the object body -> "corrupted" uploads whose size is
   slightly larger than the source, with ``x-amz-checksum-crc32:...`` text
   leaked into the tail of the file. Fix:
   ``request_checksum_calculation="when_required"``.

2. Default response checksum validation. boto3 asks for and validates
   checksums on GetObject; backends that answer with a wrong/absent header
   cause spurious validation errors. Fix:
   ``response_checksum_validation="when_required"``.

3. Virtual-hosted-style addressing (``bucket.host``). VAST VIP pools are
   usually reached by IP or a single DNS name without wildcard records, so
   ``bucket.<host>`` does not resolve. Fix: ``addressing_style="path"``.

4. Endpoint / region. VAST has no real region; SigV4 still needs one in
   the credential scope, so we pin a fixed value from config.

5. Multipart tuning. VAST recommends >= 8 MiB parts; the transfer config
   below is exposed via :func:`get_transfer_config` so the same settings
   apply to ``upload_file``/``download_file`` (and the ``s3transfer``
   manager).

Everything else is standard boto3, so this client can be passed anywhere
a normal ``botocore.client.S3`` is expected.
"""

from __future__ import annotations

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.config import Config

from .config import Settings, load_settings

MiB = 1024 * 1024


def _botocore_config(settings: Settings) -> Config:
    return Config(
        region_name=settings.region,
        signature_version="s3v4",
        s3={
            "addressing_style": "path",
            # VAST does not support S3 Accelerate / dual-stack; keep them off.
            "use_accelerate_endpoint": False,
            "use_dualstack_endpoint": False,
        },
        # --- The VAST-critical part -------------------------------------
        request_checksum_calculation="when_required",
        response_checksum_validation="when_required",
        # ----------------------------------------------------------------
        retries={"max_attempts": 5, "mode": "adaptive"},
        max_pool_connections=settings.max_pool_connections,
        connect_timeout=10,
        read_timeout=120,
        # Don't send the boto3 user-agent "feature" metrics VAST logs as noise.
        user_agent_extra="vast-s3-templates",
    )


def get_s3_client(settings: Settings | None = None):
    """Return a ``boto3`` S3 client configured for VAST."""
    settings = settings or load_settings()
    session = boto3.session.Session(
        aws_access_key_id=settings.access_key,
        aws_secret_access_key=settings.secret_key,
        region_name=settings.region,
    )
    return session.client(
        "s3",
        endpoint_url=settings.endpoint_url,
        config=_botocore_config(settings),
        verify=settings.verify_ssl,
    )


def get_s3_resource(settings: Settings | None = None):
    """Return a ``boto3`` S3 *resource* (higher-level API) configured for VAST."""
    settings = settings or load_settings()
    session = boto3.session.Session(
        aws_access_key_id=settings.access_key,
        aws_secret_access_key=settings.secret_key,
        region_name=settings.region,
    )
    return session.resource(
        "s3",
        endpoint_url=settings.endpoint_url,
        config=_botocore_config(settings),
        verify=settings.verify_ssl,
    )


def get_transfer_config(
    part_size: int = 16 * MiB,
    threshold: int = 32 * MiB,
    max_concurrency: int = 8,
) -> TransferConfig:
    """Multipart settings tuned for VAST.

    * ``multipart_threshold``: files smaller than this go up as a single PUT.
    * ``multipart_chunksize``: part size (VAST: >= 8 MiB, 16 MiB is a good default).
    * ``max_concurrency``: parallel part uploads/downloads.
    """
    return TransferConfig(
        multipart_threshold=threshold,
        multipart_chunksize=part_size,
        max_concurrency=max_concurrency,
        use_threads=True,
    )
