import os

from botocore.exceptions import EndpointConnectionError, NoCredentialsError
from dotenv import load_dotenv

from s3_client import create_s3_client

load_dotenv()


def create_bucket(bucket_name):
    """
    Create a new S3 bucket.

    Args:
        bucket_name (str): Name of the bucket to create
    """
    s3_client = create_s3_client()

    print(f"🪣 Creating bucket: '{bucket_name}'")

    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' created successfully.")
    except s3_client.exceptions.BucketAlreadyExists:
        print(f"ℹ️  Bucket '{bucket_name}' already exists.")
    except (NoCredentialsError, EndpointConnectionError) as e:
        print(f"🚫 Connection failed: {e}")
        print(f"📝 Would create bucket: '{bucket_name}' (if credentials were valid)")
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")


if __name__ == "__main__":
    bucket_name = os.getenv("VAST_BUCKET_NAME", "my-vast-bucket")
    create_bucket(bucket_name)
