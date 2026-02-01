import os
import sys
from pathlib import Path

# Add parent directory to path so we can import s3_client
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from s3_client import create_s3_client

load_dotenv()

BUCKET_NAME = os.getenv("VAST_BUCKET_NAME")
s3_client = create_s3_client()

try:
    # Check versioning status
    response = s3_client.get_bucket_versioning(Bucket=BUCKET_NAME)
    print(f"Bucket versioning status: {response.get('Status')}")

    # # Try suspending versioning temporarily
    # print("\nSuspending versioning...")
    # s3_client.put_bucket_versioning(
    #     Bucket=BUCKET_NAME,
    #     VersioningConfiguration={'Status': 'Suspended'}
    # )

    # # Check status again
    # response = s3_client.get_bucket_versioning(Bucket=BUCKET_NAME)
    # print(f"New versioning status: {response.get('Status')}")

except Exception as e:
    print(f"Error checking/modifying versioning: {e}")
