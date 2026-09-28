#!/usr/bin/env python3
"""Round-trip a pandas DataFrame through VAST as CSV and Parquet.

Two patterns are shown:

1. **Bytes in memory** via ``get_object`` / ``put_object`` — zero extra
   dependencies beyond pandas (+ pyarrow for Parquet). Works with any
   pandas reader that accepts a file-like object.

2. **``storage_options``** (pandas -> fsspec -> s3fs) — lets ``pd.read_*``
   take an ``s3://`` URL directly. s3fs is *not* hardened by our client
   factory, so we must pass the same VAST workarounds through
   ``config_kwargs``. Only used if s3fs is installed.
"""
import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from vast_s3 import get_s3_client, load_settings, ops


def main():
    settings = load_settings()
    s3 = get_s3_client(settings)
    bucket = settings.default_bucket or sys.exit("set VAST_S3_BUCKET")
    ops.create_bucket(s3, bucket)

    df = pd.DataFrame(
        {
            "id": range(1, 6),
            "city": ["Stony Brook", "Boston", "Denver", "Austin", "Seattle"],
            "temp_c": [21.5, 18.2, 25.0, 31.4, 16.8],
        }
    )

    # ---- 1. In-memory bytes ------------------------------------------------
    csv_key = "examples/cities.csv"
    ops.upload_bytes(s3, df.to_csv(index=False).encode(), bucket, csv_key, "text/csv")
    df_csv = pd.read_csv(BytesIO(ops.read_bytes(s3, bucket, csv_key)))
    print("CSV round-trip:\n", df_csv, "\n")

    pq_key = "examples/cities.parquet"
    buf = BytesIO()
    df.to_parquet(buf, index=False)
    ops.upload_bytes(s3, buf.getvalue(), bucket, pq_key, "application/vnd.apache.parquet")
    df_pq = pd.read_parquet(BytesIO(ops.read_bytes(s3, bucket, pq_key)))
    print("Parquet round-trip:\n", df_pq, "\n")
    assert df_pq.equals(df)

    # ---- 2. storage_options (optional, needs `pip install s3fs`) -----------
    try:
        import s3fs  # noqa: F401
    except ImportError:
        print("s3fs not installed; skipping storage_options example")
        return

    storage_options = {
        "key": settings.access_key,
        "secret": settings.secret_key,
        "client_kwargs": {
            "endpoint_url": settings.endpoint_url,
            "region_name": settings.region,
            "verify": settings.verify_ssl,
        },
        "config_kwargs": {
            "signature_version": "s3v4",
            "s3": {"addressing_style": "path"},
            "request_checksum_calculation": "when_required",
            "response_checksum_validation": "when_required",
        },
    }
    df_fs = pd.read_parquet(f"s3://{bucket}/{pq_key}", storage_options=storage_options)
    print("storage_options round-trip:\n", df_fs)


if __name__ == "__main__":
    main()
