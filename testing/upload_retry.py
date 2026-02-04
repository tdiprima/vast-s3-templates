import os
import sys
import time
from pathlib import Path
from random import uniform

from botocore.exceptions import (ClientError, EndpointConnectionError, NoCredentialsError)
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))

from s3_client import create_s3_client

load_dotenv()


def test_connection(s3_client):
    """
    Test the S3 connection by attempting to list buckets.
    
    Args:
        s3_client: Configured S3 client
        
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        s3_client.list_buckets()
        print("🔗 S3 connection test successful")
        return True
    except (NoCredentialsError, EndpointConnectionError) as e:
        print(f"🚫 Connection test failed: {e}")
        return False
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code in ('InvalidAccessKeyId', 'SignatureDoesNotMatch', 'AccessDenied'):
            print(f"🔐 Authentication failed: {e.response.get('Error', {}).get('Message', str(e))}")
        else:
            print(f"⚠️  Connection test returned error: {e.response.get('Error', {}).get('Message', str(e))}")
        return False
    except Exception as e:
        print(f"❌ Unexpected connection test error: {e}")
        return False


def upload_object(bucket_name, object_key, file_content, max_retries=3):
    """
    Upload an object to an S3 bucket with retry logic for internal errors.

    Args:
        bucket_name (str): Name of the bucket
        object_key (str): The key (path) for the object in the bucket
        file_content (bytes): Content to upload
        max_retries (int): Maximum number of retry attempts for internal errors
    """
    s3_client = create_s3_client()

    print(f"📤 Uploading '{object_key}' to bucket '{bucket_name}'")
    print(f"   Content size: {len(file_content)} bytes")

    for attempt in range(max_retries + 1):
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
            return response
        except (NoCredentialsError, EndpointConnectionError) as e:
            print(f"🚫 Connection failed: {e}")
            print(
                f"📝 Would upload '{object_key}' with {len(file_content)} bytes (if credentials were valid)"
            )
            break
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            if error_code == 'InternalError' and attempt < max_retries:
                # Exponential backoff with jitter
                wait_time = (2 ** attempt) + uniform(0, 1)  # nosec B311
                print(f"⚠️  Internal server error (attempt {attempt + 1}/{max_retries + 1}). Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Error uploading object: {error_message}")
                if error_code:
                    print(f"   Error code: {error_code}")
                break
        except Exception as e:
            print(f"❌ Unexpected error uploading object: {e}")
            break


if __name__ == "__main__":
    bucket_name = os.getenv("VAST_BUCKET_NAME", "my-vast-bucket")
    object_key = "Tammy-File.txt"
    file_content = b"This is some sample data for Vast S3."

    # Test connection first
    s3_client = create_s3_client()
    if not test_connection(s3_client):
        print("\n❌ Skipping upload due to connection issues")
        exit(1)
    
    print()  # Add spacing
    upload_object(bucket_name, object_key, file_content)
