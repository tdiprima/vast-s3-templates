# vast-s3-templates

boto3 templates that actually work against **VAST Data** S3.

⭐️ Connect to the VPN and run.

Stock `boto3 >= 1.36` breaks against VAST (and most non-AWS S3 backends):
uploads come back a few bytes larger than the source with
`x-amz-checksum-crc32:…` text leaked into the tail of the object, and
downloads can fail checksum validation. This repo ships a hardened client
factory that turns those AWS-only behaviours off, plus copy-paste scripts
for the everyday operations.

Tested with **boto3 1.43.103**, pandas 3.0, pyarrow 25, Python 3.10+.

## What the hardened client fixes

| Problem on VAST | Cause (boto3 default) | Fix in `vast_s3/client.py` |
|---|---|---|
| Corrupted uploads, size off by ~40–60 bytes, `x-amz-checksum-crc32` inside the file | Trailing CRC32 checksum sent with `Content-Encoding: aws-chunked` | `request_checksum_calculation="when_required"` |
| Spurious "checksum mismatch" on GET | Client requests + validates response checksums | `response_checksum_validation="when_required"` |
| `bucket.vast-host` DNS failures | Virtual-hosted addressing | `addressing_style="path"` |
| `SignatureDoesNotMatch` / region errors | Missing region in SigV4 scope | Pinned `signature_version="s3v4"` + `VAST_S3_REGION` |
| Slow / failing big uploads | Tiny 8 MiB parts, low concurrency | `get_transfer_config()` → 16 MiB parts, 8 threads |

Everything else is plain boto3, so the returned object is a normal S3 client.

## Setup

```bash
git clone <this repo> && cd vast-s3-templates
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # or: pip install -e ".[pandas]"
cp .env.example .env                   # then edit
```

`.env`:

```dotenv
VAST_S3_ENDPOINT=https://vast-s3.example.edu   # VIP pool DNS name or IP, with scheme
VAST_S3_ACCESS_KEY=...
VAST_S3_SECRET_KEY=...
VAST_S3_BUCKET=my-bucket                        # optional default for the scripts
#VAST_S3_CA_BUNDLE=/path/to/ca.pem              # self-signed cert
#VAST_S3_VERIFY_SSL=false                       # dev only
```

## Use the client in your own code

```python
from vast_s3 import get_s3_client, get_transfer_config

s3 = get_s3_client()                      # reads .env / environment
s3.upload_file("big.bin", "my-bucket", "raw/big.bin", Config=get_transfer_config())
print(s3.get_object(Bucket="my-bucket", Key="raw/big.bin")["ContentLength"])
```

Higher-level helpers (pagination, batch delete, presigning, versioning) live
in `vast_s3/ops.py`; the scripts below are thin CLIs over them.

## Scripts

All scripts accept `-b/--bucket` (falls back to `VAST_S3_BUCKET`) and `-h`.

```bash
python scripts/create_bucket.py -b data --versioning
python scripts/list_objects.py --buckets
python scripts/list_objects.py raw/                       # objects under a prefix

python scripts/upload.py file.csv -p raw/                 # -> raw/file.csv
python scripts/upload.py ./dataset/ -p raw/dataset/       # recursive
python scripts/upload.py file.csv -k exact/key.csv

python scripts/download.py raw/file.csv ./out/            # single object
python scripts/download.py raw/ ./out/ -r                 # whole prefix

python scripts/presigned_url.py raw/file.csv -e 900       # GET URL, 15 min
python scripts/presigned_url.py incoming/x.bin --put      # PUT URL

python scripts/versioning.py status
python scripts/versioning.py enable
python scripts/versioning.py list raw/
python scripts/versioning.py restore raw/file.csv <version-id>

python scripts/delete.py raw/file.csv
python scripts/delete.py raw/ -r -y                       # everything under prefix
python scripts/delete.py --bucket-too -y                  # empty bucket
```

## pandas example

```bash
pip install -e ".[pandas]"
python examples/pandas_load.py
```

Shows CSV and Parquet round-trips through memory (`get_object`/`put_object`),
and, if `s3fs` is installed, `pd.read_parquet("s3://…", storage_options=…)`
with the same VAST workarounds passed through `config_kwargs`.

## Tests

Runs the scripts end to end against a local
[moto](https://github.com/getmoto/moto) server, including a 40 MiB multipart
upload byte-compared after download.

```bash
pip install -e ".[test]"
pytest
```

## Notes on VAST specifics

* **No `LocationConstraint`.** `create_bucket` is called without a
  `CreateBucketConfiguration`; VAST rejects it.
* **Region is cosmetic.** Any value works, but it must be the same on every
  client that signs URLs, or presigned URLs will fail.
* **Presigned URLs** embed `VAST_S3_ENDPOINT`. Use the DNS name your
  recipients can reach, not an internal VIP.
* **Object versioning** must be enabled per bucket *and* the VAST view must
  have S3 versioning allowed. `versioning.py status` tells you the bucket
  side.
* **Other S3-compatible stores** (MinIO, Ceph RGW, Wasabi, etc.) have the same
  checksum problem; this client works unchanged against them.
