import boto3
from botocore.client import Config
from icecream import ic

# Replace these with your creds + endpoint
ACCESS_KEY = "XFNWX8S9QRC4WQTWVTRJ"
SECRET_KEY = "MwLZfoeOrxiCALYisYRuu7MSCX4x76nbIQYc/ZIt"
ENDPOINT_URL = "https://research-shares.res-vast1.uhmc.sunysb.edu"
# aws --endpoint-url=https://research-shares.res-vast1.uhmc.sunysb.edu s3 ls s3://bmi-dev-area/

# Amazon S3 (Simple Storage Service)

# Create S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    endpoint_url=ENDPOINT_URL,  # <--- custom S3 (not AWS)
    region_name='us-east-1',
    config=Config(signature_version="s3v4"),
    use_ssl=True,
)

# Test: list buckets
try:
    response = s3.list_buckets()
    ic(response)
    print("✅ Auth worked!")
    for bucket in response.get("Buckets", []):
        print(f"{bucket['Name']}")
except Exception as e:
    print("❌ Failed to connect:", e)
