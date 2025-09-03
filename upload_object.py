import os

from botocore.exceptions import EndpointConnectionError, NoCredentialsError
from dotenv import load_dotenv

from s3_client import create_s3_client

load_dotenv()


def upload_object(bucket_name, object_key, file_content):
    """
    Upload an object to an S3 bucket.

    Args:
        bucket_name (str): Name of the bucket
        object_key (str): The key (path) for the object in the bucket
        file_content (bytes): Content to upload
    """
    s3_client = create_s3_client()

    print(f"📤 Uploading '{object_key}' to bucket '{bucket_name}'")
    print(f"   Content size: {len(file_content)} bytes")

    try:
        # Use put_object without any checksum parameters
        # Don't specify ChecksumAlgorithm or any checksum-related parameters
        response = s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=file_content,
            # Explicitly set content length to avoid chunked encoding
            ContentLength=len(file_content),
        )
        print(f"✅ Object '{object_key}' uploaded successfully.")
        print(f"   ETag: {response.get('ETag', 'N/A')}")
    except (NoCredentialsError, EndpointConnectionError) as e:
        print(f"🚫 Connection failed: {e}")
        print(
            f"📝 Would upload '{object_key}' with {len(file_content)} bytes (if credentials were valid)"
        )
    except Exception as e:
        print(f"❌ Error uploading object: {e}")


if __name__ == "__main__":
    bucket_name = os.getenv("VAST_BUCKET_NAME", "my-vast-bucket")
    object_key = "Tammy-File.txt"
    file_content = b"This is some sample data for Vast S3."

    upload_object(bucket_name, object_key, file_content)
