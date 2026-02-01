import os

from botocore.exceptions import EndpointConnectionError, NoCredentialsError
from dotenv import load_dotenv

from s3_client import create_s3_client

load_dotenv()


def list_objects(bucket_name):
    """
    List all objects in an S3 bucket using the V1 API for VAST compatibility.

    Args:
        bucket_name (str): Name of the bucket to list objects from
    """
    s3_client = create_s3_client()

    print(f"📁 Listing objects in bucket '{bucket_name}'")

    try:
        # Use list_objects (V1) instead of list_objects_v2
        # V1 is more widely supported by S3-compatible systems
        response = s3_client.list_objects(Bucket=bucket_name)

        if "Contents" in response:
            print(f"  Found {len(response['Contents'])} objects:")
            for obj in response["Contents"]:
                print(
                    f"  📄 {obj['Key']} | {obj['Size']} bytes | {obj['LastModified']}"
                )
        else:
            print("  💭 No objects found in bucket.")

    except (NoCredentialsError, EndpointConnectionError) as e:
        print(f"🚫 Connection failed: {e}")
        print(f"📝 Would list objects in '{bucket_name}' (if credentials were valid)")
    except Exception as e:
        # If V1 also fails, try a more basic approach
        print(f"⚠️  Standard list failed: {e}")
        print("Trying alternative method...")
        try:
            # Try with minimal parameters
            response = s3_client.list_objects(
                Bucket=bucket_name, MaxKeys=1000  # Explicit limit
            )
            if "Contents" in response:
                print(f"  Found {len(response['Contents'])} objects:")
                for obj in response["Contents"]:
                    print(
                        f"  📄 {obj['Key']} | {obj['Size']} bytes | {obj['LastModified']}"
                    )
            else:
                print("  💭 No objects found in bucket.")
        except Exception as e2:
            print(f"❌ Error listing objects: {e2}")


if __name__ == "__main__":
    bucket_name = os.getenv("VAST_BUCKET_NAME", "my-vast-bucket")
    list_objects(bucket_name)
