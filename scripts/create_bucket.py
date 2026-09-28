#!/usr/bin/env python3
"""Create a bucket on VAST (idempotent)."""
import _bootstrap  # noqa: F401

from vast_s3 import ops
from vast_s3._cli import parser, resolve


def main():
    p = parser("Create a bucket")
    p.add_argument("-v", "--versioning", action="store_true", help="enable versioning")
    args = p.parse_args()
    s3, bucket = resolve(args)

    created = ops.create_bucket(s3, bucket)
    print(f"{'created' if created else 'exists '} {bucket}")
    if args.versioning:
        ops.set_versioning(s3, bucket, True)
        print(f"versioning enabled on {bucket}")


if __name__ == "__main__":
    main()
