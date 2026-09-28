#!/usr/bin/env python3
"""Generate a presigned GET (download) or PUT (upload) URL.

The URL is signed for the endpoint in VAST_S3_ENDPOINT, so the recipient
must be able to reach that host. Test with:

    curl -o out.bin "<get url>"
    curl -T file.bin "<put url>"
"""
import _bootstrap  # noqa: F401

from vast_s3 import ops
from vast_s3._cli import parser, resolve


def main():
    p = parser("Create a presigned URL")
    p.add_argument("key")
    p.add_argument("--put", action="store_true", help="sign an upload instead of a download")
    p.add_argument("--content-type", help="required Content-Type for PUT (optional)")
    p.add_argument("-e", "--expires", type=int, default=3600, help="seconds (default 3600)")
    args = p.parse_args()
    s3, bucket = resolve(args)

    if args.put:
        url = ops.presigned_put_url(s3, bucket, args.key, args.expires, args.content_type)
    else:
        url = ops.presigned_get_url(s3, bucket, args.key, args.expires)
    print(url)


if __name__ == "__main__":
    main()
