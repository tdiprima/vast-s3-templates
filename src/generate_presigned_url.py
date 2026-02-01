import os

from botocore.exceptions import EndpointConnectionError, NoCredentialsError
from dotenv import load_dotenv

from s3_client import create_s3_client

load_dotenv()


def generate_presigned_url(bucket_name, object_key, expiration=3600):
    """
    Generate a presigned URL for an S3 object.

    Args:
        bucket_name (str): Name of the bucket
        object_key (str): The key (path) for the object
        expiration (int): URL expiration time in seconds (default: 1 hour)

    Returns:
        str: Presigned URL
    """
    s3_client = create_s3_client()

    print(f"🔗 Generating presigned URL for '{object_key}' in bucket '{bucket_name}'")
    print(
        f"   Expiration: {expiration} seconds ({expiration//3600}h {(expiration%3600)//60}m)"
    )

    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=expiration,
        )
        print("✅ Presigned URL generated:")
        print(f"   {presigned_url}")
        return presigned_url
    except (NoCredentialsError, EndpointConnectionError) as e:
        print(f"🚫 Connection failed: {e}")
        print(
            f"📝 Would generate presigned URL for '{object_key}' (if credentials were valid)"
        )
        return None
    except Exception as e:
        print(f"❌ Error generating presigned URL: {e}")
        return None


if __name__ == "__main__":
    bucket_name = os.getenv("VAST_BUCKET_NAME", "my-vast-bucket")
    object_key = "example.txt"
    generate_presigned_url(bucket_name, object_key)
