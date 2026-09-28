#!/usr/bin/env python3
"""Upload one or more files (multipart for large files)."""
import _bootstrap  # noqa: F401

import mimetypes
from pathlib import Path

from vast_s3 import ops
from vast_s3._cli import fmt_size, parser, resolve


def main():
    p = parser("Upload file(s) to VAST")
    p.add_argument("paths", nargs="+", help="local file(s) or directory")
    p.add_argument("-p", "--prefix", default="", help="key prefix, e.g. data/raw/")
    p.add_argument("-k", "--key", help="explicit key (single file only)")
    args = p.parse_args()
    s3, bucket = resolve(args)

    files = []
    for raw in args.paths:
        path = Path(raw)
        if path.is_dir():
            files += [(f, f.relative_to(path).as_posix()) for f in path.rglob("*") if f.is_file()]
        else:
            files.append((path, path.name))

    if args.key and len(files) != 1:
        raise SystemExit("--key only valid with a single file")

    for path, rel in files:
        key = args.key or f"{args.prefix}{rel}"
        ctype = mimetypes.guess_type(path.name)[0]
        ops.upload_file(s3, path, bucket, key, content_type=ctype)
        print(f"{fmt_size(path.stat().st_size):>10}  s3://{bucket}/{key}")


if __name__ == "__main__":
    main()
