from botocore.exceptions import EndpointConnectionError, NoCredentialsError

from s3_client import create_s3_client


def list_objects(bucket_name):
    """
    List all objects in an S3 bucket.

    Args:
        bucket_name (str): Name of the bucket to list objects from
    """
    s3_client = create_s3_client()

    print(f"📁 Listing objects in bucket '{bucket_name}'")

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if "Contents" in response:
            for obj in response["Contents"]:
                print(
                    f"  📄 {obj['Key']} | {obj['Size']} bytes | {obj['LastModified']}"
                )
        else:
            print(f"  💭 No objects found in bucket.")
    except (NoCredentialsError, EndpointConnectionError) as e:
        print(f"🚫 Connection failed: {e}")
        print(f"📝 Would list objects in '{bucket_name}' (if credentials were valid)")
    except Exception as e:
        print(f"❌ Error listing objects: {e}")


if __name__ == "__main__":
    bucket_name = "my-vast-bucket"
    list_objects(bucket_name)
