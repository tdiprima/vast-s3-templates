"""
The corruption is happening with regular file uploads too - the S3 storage is definitely
adding metadata (c\r\n prefix and checksum suffix) to all files.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add parent directory to path so we can import s3_client
sys.path.append(str(Path(__file__).parent.parent))

from s3_client import create_s3_client

load_dotenv()

BUCKET_NAME = os.getenv("VAST_BUCKET_NAME")
LOCAL_FILE = "testing.txt"
S3_KEY = "uploads/testing.txt"

s3_client = create_s3_client()

# Read local file content
file_content = Path(LOCAL_FILE).read_text()

print("Original file content:")
print(repr(file_content))

try:
    # Upload to S3
    with open(LOCAL_FILE, "rb") as f:
        s3_client.upload_fileobj(
            f, BUCKET_NAME, S3_KEY, ExtraArgs={"ContentType": "text/plain"}
        )

    print(f"\nFile uploaded to: s3://{BUCKET_NAME}/{S3_KEY}")

    # Download and read back
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=S3_KEY)
    downloaded_content = response["Body"].read().decode("utf-8")

    print("\nDownloaded content from S3:")
    print(repr(downloaded_content))

    print("\nContent match:", file_content == downloaded_content)

except Exception as e:
    print(f"❌ Error uploading file: {e}")
