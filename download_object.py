from botocore.exceptions import EndpointConnectionError, NoCredentialsError

from s3_client import create_s3_client


def download_object(bucket_name, object_key, local_file_path):
    """
    Download an object from an S3 bucket.

    Args:
        bucket_name (str): Name of the bucket
        object_key (str): The key (path) for the object in the bucket
        local_file_path (str): Local path to save the downloaded file
    """
    s3_client = create_s3_client()

    print(
        f"📥 Downloading '{object_key}' from bucket '{bucket_name}' to '{local_file_path}'"
    )

    try:
        s3_client.download_file(
            Bucket=bucket_name, Key=object_key, Filename=local_file_path
        )
        print(f"✅ Object '{object_key}' downloaded successfully.")
    except (NoCredentialsError, EndpointConnectionError) as e:
        print(f"🚫 Connection failed: {e}")
        print(
            f"📝 Would download '{object_key}' to '{local_file_path}' (if credentials were valid)"
        )
    except Exception as e:
        print(f"❌ Error downloading object: {e}")


if __name__ == "__main__":
    bucket_name = "my-vast-bucket"
    object_key = "example.txt"
    local_file_path = "downloaded_example.txt"

    download_object(bucket_name, object_key, local_file_path)
