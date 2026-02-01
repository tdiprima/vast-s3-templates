import os

import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()


def create_s3_client():
    """
    Configure and return an S3 client for Vast S3 with all advanced features disabled.
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

    # Create a minimal configuration
    config = Config(
        signature_version="s3v4",
        s3={
            "payload_signing_enabled": False,
            "addressing_style": "path",
            "use_accelerate_endpoint": False,
        },
        # Disable retries to see errors immediately
        retries={"max_attempts": 0},
    )

    # Create the client
    s3_client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        config=config,
        # Disable all optional S3 features
        use_ssl=True,
        verify=True,
    )

    # Monkey patch to disable all checksum algorithms
    original_make_request = s3_client._make_request

    def patched_make_request(operation_model, request_dict, request_context):
        # Remove problematic headers before sending
        headers_to_remove = [
            "x-amz-sdk-checksum-algorithm",
            "x-amz-trailer",
            "x-amz-decoded-content-length",
            "content-encoding",
            "transfer-encoding",
            "expect",
        ]

        if "headers" in request_dict:
            for header in headers_to_remove:
                request_dict["headers"].pop(header, None)
                request_dict["headers"].pop(header.title(), None)
                request_dict["headers"].pop(header.upper(), None)

        # Ensure we're not using chunked encoding
        if "body" in request_dict and hasattr(request_dict["body"], "read"):
            # If it's a file-like object, read it into memory
            content = request_dict["body"].read()
            if hasattr(request_dict["body"], "seek"):
                request_dict["body"].seek(0)  # Reset for potential retry
            request_dict["body"] = content
            request_dict["headers"]["Content-Length"] = str(len(content))

        return original_make_request(operation_model, request_dict, request_context)

    s3_client._make_request = patched_make_request

    return s3_client
