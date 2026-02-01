import os

from botocore.exceptions import EndpointConnectionError, NoCredentialsError
from dotenv import load_dotenv

from s3_client import create_s3_client

load_dotenv()


def delete_object(bucket_name, object_key):
    """
    Delete a single object from an S3 bucket.

    Args:
        bucket_name (str): Name of the bucket
        object_key (str): The key (path) for the object to delete
    """
    s3_client = create_s3_client()

    print(f"🗑️ Deleting object '{object_key}' from bucket '{bucket_name}'")

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        print(f"✅ Object '{object_key}' deleted successfully.")
    except (NoCredentialsError, EndpointConnectionError) as e:
        print(f"🚫 Connection failed: {e}")
        print(f"📝 Would delete '{object_key}' (if credentials were valid)")
    except Exception as e:
        print(f"❌ Error deleting object: {e}")


def delete_bucket(bucket_name):
    """
    Delete an entire S3 bucket (ensure it's empty first).

    Args:
        bucket_name (str): Name of the bucket to delete
    """
    s3_client = create_s3_client()

    print(f"⚠️ Deleting entire bucket '{bucket_name}' (ensure it's empty first!)")

    try:
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' deleted successfully.")
    except (NoCredentialsError, EndpointConnectionError) as e:
        print(f"🚫 Connection failed: {e}")
        print(f"📝 Would delete bucket '{bucket_name}' (if credentials were valid)")
    except Exception as e:
        print(f"❌ Error deleting bucket: {e}")


if __name__ == "__main__":
    bucket_name = os.getenv("VAST_BUCKET_NAME", "my-vast-bucket")
    object_key = "example.txt"

    # Delete a single object
    delete_object(bucket_name, object_key)

    # Delete the entire bucket (ensure it's empty first)
    # delete_bucket(bucket_name)
