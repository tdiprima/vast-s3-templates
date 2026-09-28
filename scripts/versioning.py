#!/usr/bin/env python3
"""Enable/suspend/inspect bucket versioning and list object versions."""
import _bootstrap  # noqa: F401

from vast_s3 import ops
from vast_s3._cli import fmt_size, parser, resolve


def main():
    p = parser("Bucket versioning")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="show versioning status")
    sub.add_parser("enable", help="enable versioning")
    sub.add_parser("suspend", help="suspend versioning")
    ls = sub.add_parser("list", help="list object versions")
    ls.add_argument("prefix", nargs="?", default="")
    rs = sub.add_parser("restore", help="copy an old version back as the latest")
    rs.add_argument("key")
    rs.add_argument("version_id")
    args = p.parse_args()
    s3, bucket = resolve(args)

    if args.cmd == "status":
        print(f"{bucket}: {ops.get_versioning(s3, bucket)}")
    elif args.cmd == "enable":
        ops.set_versioning(s3, bucket, True)
        print(f"{bucket}: Enabled")
    elif args.cmd == "suspend":
        ops.set_versioning(s3, bucket, False)
        print(f"{bucket}: Suspended")
    elif args.cmd == "list":
        for v in ops.list_versions(s3, bucket, args.prefix):
            latest = "*" if v.get("IsLatest") else " "
            size = fmt_size(v["Size"]) if v["Kind"] == "version" else "(delete marker)"
            print(f"{latest} {v['LastModified']:%Y-%m-%d %H:%M}  {size:>16}  "
                  f"{v['VersionId']}  {v['Key']}")
    elif args.cmd == "restore":
        s3.copy_object(
            Bucket=bucket,
            Key=args.key,
            CopySource={"Bucket": bucket, "Key": args.key, "VersionId": args.version_id},
            MetadataDirective="COPY",
        )
        print(f"restored {args.key} from version {args.version_id}")


if __name__ == "__main__":
    main()
