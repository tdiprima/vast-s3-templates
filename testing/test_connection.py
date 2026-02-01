import os
import sys
from pathlib import Path

# Add parent directory to path so we can import s3_client
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from s3_client import create_s3_client

load_dotenv()


def test_s3_connection():
    """Test S3 connection with different approaches."""
    s3_client = create_s3_client()
    bucket_name = os.getenv("VAST_BUCKET_NAME", "my-vast-bucket")

    print("🧪 Testing S3 connection...")
    print(f"   Bucket: {bucket_name}")

    # Test 1: Try to list all buckets (this doesn't require a specific bucket)
    print("\n1️⃣ Testing list_buckets()...")
    try:
        response = s3_client.list_buckets()
        print("✅ list_buckets() successful!")
        if "Buckets" in response:
            for bucket in response["Buckets"]:
                print(f"   Found bucket: {bucket['Name']}")
        else:
            print("   No buckets found.")
    except Exception as e:
        print(f"❌ list_buckets() failed: {e}")

    # Test 2: Try with empty bucket name - of course this will fail
    # print("\n2️⃣ Testing list_objects_v2() with empty bucket...")
    # try:
    #     response = s3_client.list_objects_v2(Bucket='')
    #     print("✅ Empty bucket name worked!")
    #     if 'Contents' in response:
    #         for obj in response['Contents']:
    #             print(f"   Object: {obj['Key']}")
    # except Exception as e:
    #     print(f"❌ Empty bucket failed: {e}")

    # Test 3: Try with original bucket name
    print(f"\n3️⃣ Testing list_objects_v2() with bucket '{bucket_name}'...")
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        print("✅ Original bucket name worked!")
        if "Contents" in response:
            for obj in response["Contents"]:
                print(f"   Object: {obj['Key']}")
    except Exception as e:
        print(f"❌ Original bucket failed: {e}")


if __name__ == "__main__":
    test_s3_connection()
