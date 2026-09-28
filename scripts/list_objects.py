#!/usr/bin/env python3
"""List buckets, or objects under a prefix."""
import _bootstrap  # noqa: F401

from vast_s3 import ops
from vast_s3._cli import fmt_size, parser, resolve


def main():
    p = parser("List buckets or objects")
    p.add_argument("prefix", nargs="?", default="", help="key prefix filter")
    p.add_argument("--buckets", action="store_true", help="list buckets instead")
    args = p.parse_args()

    if args.buckets:
        args.bucket = "-"  # avoid the missing-bucket error
        s3, _ = resolve(args)
        for b in s3.list_buckets()["Buckets"]:
            print(f"{b['CreationDate']:%Y-%m-%d %H:%M}  {b['Name']}")
        return

    s3, bucket = resolve(args)
    total = count = 0
    for obj in ops.list_objects(s3, bucket, args.prefix):
        count += 1
        total += obj["Size"]
        print(f"{obj['LastModified']:%Y-%m-%d %H:%M}  {fmt_size(obj['Size']):>10}  {obj['Key']}")
    print(f"-- {count} objects, {fmt_size(total)}")


if __name__ == "__main__":
    main()
