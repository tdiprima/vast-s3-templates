#!/usr/bin/env python3
"""Download an object, or every object under a prefix."""
import _bootstrap  # noqa: F401

from pathlib import Path

from vast_s3 import ops
from vast_s3._cli import fmt_size, parser, resolve


def main():
    p = parser("Download from VAST")
    p.add_argument("key", help="object key, or prefix when --recursive")
    p.add_argument("dest", nargs="?", default=".", help="local file or directory")
    p.add_argument("-r", "--recursive", action="store_true", help="treat key as prefix")
    args = p.parse_args()
    s3, bucket = resolve(args)

    if not args.recursive:
        out = ops.download_file(s3, bucket, args.key, args.dest)
        print(f"{fmt_size(out.stat().st_size):>10}  {out}")
        return

    dest = Path(args.dest)
    for obj in ops.list_objects(s3, bucket, args.key):
        rel = obj["Key"][len(args.key):].lstrip("/") or Path(obj["Key"]).name
        out = ops.download_file(s3, bucket, obj["Key"], dest / rel)
        print(f"{fmt_size(obj['Size']):>10}  {out}")


if __name__ == "__main__":
    main()
