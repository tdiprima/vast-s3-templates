# VAST S3 Templates

Ready-to-use Python templates for working with VAST Data's S3-compatible object storage.

## Why VAST S3 Is Different

VAST Data exposes an S3-compatible API, but "compatible" does a lot of heavy lifting. Standard boto3 clients send checksum headers, chunked transfer encoding, and API calls that VAST doesn't fully support. The result: uploads get corrupted with injected metadata, downloads come back with `x-amz-` prefixes in the content, and `list_objects_v2` calls fail silently.

If you've ever pulled a CSV from VAST and found `c\r\n` prepended to your data, you've hit this.

## What This Repo Does

This project provides a battle-tested S3 client factory (`s3_client.py`) that neutralizes VAST's compatibility gaps at the connection level, so every script you build on top of it just works. The client:

- Forces SigV4 signing with path-style addressing
- Strips problematic checksum and transfer-encoding headers before every request
- Reads file-like bodies into memory to prevent chunked encoding corruption
- Uses adaptive retry with up to 3 attempts

On top of that client, the repo includes standalone scripts for common S3 operations: creating buckets, uploading and downloading objects, listing contents, deleting resources, generating presigned URLs, enabling versioning, and loading data directly into pandas DataFrames.

## Quick Example

Upload a file and read it back into a DataFrame:

```python
from s3_client import create_s3_client
import pandas as pd
from io import StringIO

s3 = create_s3_client()

# Upload
s3.put_object(
    Bucket="my-bucket",
    Key="data/results.csv",
    Body=open("results.csv", "rb").read(),
    ContentType="text/csv"
)

# Download into pandas
response = s3.get_object(Bucket="my-bucket", Key="data/results.csv")
df = pd.read_csv(StringIO(response["Body"].read().decode("utf-8")))
print(df.head())
```

## Getting Started

**Prerequisites:** Python 3.11+

**Install dependencies:**

```bash
pip install boto3 botocore python-dotenv pandas
```

**Configure credentials** by creating a `.env` file in the project root:

```
VAST_S3_ENDPOINT=https://your-vast-endpoint.example.com
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
VAST_BUCKET_NAME=my-vast-bucket
```

**Run any script directly:**

```bash
cd src

# Create a bucket
python create_bucket.py

# Upload an object
python upload_object.py

# List objects
python list_objects.py

# Download an object
python download_object.py

# Generate a presigned URL
python generate_presigned_url.py

# Enable bucket versioning
python bucket_versioning.py

# Upload CSV and load into pandas
python vast_s3_data_loader.py
```

Each script works standalone and reads configuration from environment variables.

## Available Templates

| Script | What It Does |
|---|---|
| `s3_client.py` | Configures a VAST-compatible boto3 S3 client |
| `create_bucket.py` | Creates a new S3 bucket |
| `upload_object.py` | Uploads an object with explicit content-length handling |
| `download_object.py` | Downloads an object to the local filesystem |
| `list_objects.py` | Lists all objects in a bucket (uses V1 API for compatibility) |
| `delete_objects.py` | Deletes individual objects or entire buckets |
| `generate_presigned_url.py` | Creates time-limited download URLs |
| `bucket_versioning.py` | Enables versioning on a bucket |
| `vast_s3_data_loader.py` | End-to-end example: upload CSV, download, load into pandas |

## License

[MIT](LICENSE)

<BR>
