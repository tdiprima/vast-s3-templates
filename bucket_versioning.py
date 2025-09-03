import os

from botocore.exceptions import EndpointConnectionError, NoCredentialsError
from dotenv import load_dotenv

from s3_client import create_s3_client

load_dotenv()


def enable_bucket_versioning(bucket_name):
    """
    Enable versioning for an S3 bucket.

    Args:
        bucket_name (str): Name of the bucket to enable versioning for
    """
    s3_client = create_s3_client()

    print(f"🔄 Enabling versioning for bucket '{bucket_name}'")

    try:
        s3_client.put_bucket_versioning(
            Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"}
        )
        print(f"✅ Versioning enabled for bucket '{bucket_name}' successfully.")
    except (NoCredentialsError, EndpointConnectionError) as e:
        print(f"🚫 Connection failed: {e}")
        print(
            f"📝 Would enable versioning for '{bucket_name}' (if credentials were valid)"
        )
    except Exception as e:
        print(f"❌ Error enabling versioning: {e}")


if __name__ == "__main__":
    bucket_name = os.getenv("VAST_BUCKET_NAME", "my-vast-bucket")
    enable_bucket_versioning(bucket_name)
