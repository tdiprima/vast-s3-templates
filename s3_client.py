import os

import boto3


def create_s3_client():
    """
    Configure and return an S3 client for Vast S3.
    Uses environment variables or demo defaults.

    Environment variables:
    - VAST_S3_ENDPOINT: S3 endpoint URL
    - AWS_ACCESS_KEY_ID: Access key
    - AWS_SECRET_ACCESS_KEY: Secret key

    Returns:
        boto3.client: Configured S3 client
    """
    endpoint_url = os.getenv(
        "VAST_S3_ENDPOINT", "https://your-vast-s3-endpoint.example.com"
    )
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "YOUR_ACCESS_KEY")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "YOUR_SECRET_KEY")

    if access_key == "YOUR_ACCESS_KEY":
        print("⚠️  Using demo credentials. Set environment variables for real usage:")
        print("   export VAST_S3_ENDPOINT='https://your-endpoint.com'")
        print("   export AWS_ACCESS_KEY_ID='your-access-key'")
        print("   export AWS_SECRET_ACCESS_KEY='your-secret-key'")
        print()

    s3_client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return s3_client
