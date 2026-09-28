#!/usr/bin/env python3
"""Delete an object, a prefix, or an (empty) bucket."""
import _bootstrap  # noqa: F401

from vast_s3 import ops
from vast_s3._cli import parser, resolve


def main():
    p = parser("Delete objects or a bucket")
    p.add_argument("key", nargs="?", default="", help="object key (or prefix with -r)")
    p.add_argument("-r", "--recursive", action="store_true", help="delete everything under prefix")
    p.add_argument("--version-id", help="delete a specific version")
    p.add_argument("--bucket-too", action="store_true",
                   help="also delete the bucket (must be empty after)")
    p.add_argument("-y", "--yes", action="store_true", help="skip confirmation")
    args = p.parse_args()
    s3, bucket = resolve(args)

    if args.recursive:
        target = f"s3://{bucket}/{args.key}* (recursive)"
    elif args.key:
        target = f"s3://{bucket}/{args.key}"
    elif args.bucket_too:
        target = f"bucket {bucket}"
    else:
        raise SystemExit("nothing to delete: give a key, -r prefix, or --bucket-too")

    if not args.yes and input(f"delete {target}? [y/N] ").lower() != "y":
        raise SystemExit("aborted")

    if args.recursive:
        n = ops.delete_prefix(s3, bucket, args.key)
        print(f"deleted {n} objects")
    elif args.key:
        ops.delete_object(s3, bucket, args.key, args.version_id)
        print(f"deleted {target}")

    if args.bucket_too:
        s3.delete_bucket(Bucket=bucket)
        print(f"deleted bucket {bucket}")


if __name__ == "__main__":
    main()
