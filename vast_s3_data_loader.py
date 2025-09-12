import os
from io import StringIO

import pandas as pd
from dotenv import load_dotenv

from s3_client import create_s3_client

load_dotenv()

ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
ENDPOINT_URL = os.getenv("VAST_S3_ENDPOINT")  # Vast S3 endpoint
BUCKET_NAME = os.getenv("VAST_BUCKET_NAME")
OBJECT_KEY = "training_data/sample_dataset.csv"  # Path in the bucket

s3_client = create_s3_client()

sample_data = """id,name,age
1,Alice,30
2,Bob,25
3,Charlie,35
"""

print("Sample data being uploaded:")
print(repr(sample_data))

s3_client.put_object(
    Bucket=BUCKET_NAME, Key=OBJECT_KEY, Body=sample_data, ContentType="text/csv"
)
print(f"Sample data uploaded to Vast S3: s3://{BUCKET_NAME}/{OBJECT_KEY}")

response = s3_client.get_object(Bucket=BUCKET_NAME, Key=OBJECT_KEY)
raw_content = response["Body"].read().decode("utf-8")
print("\nRaw content from S3:")
print(repr(raw_content))

csv_content = raw_content.split("\n")
csv_lines = [
    line.strip()
    for line in csv_content
    if line.strip() and "," in line and not line.startswith("x-amz-")
]

clean_csv = "\n".join(csv_lines)
print("\nCleaned CSV content:")
print(repr(clean_csv))

df = pd.read_csv(StringIO(clean_csv))

print("\nLoaded DataFrame from Vast S3:")
print(df.head())
print(f"\nColumn names: {df.columns.tolist()}")
print(f"Column dtypes: {df.dtypes}")

df.columns = df.columns.str.strip()

average_age = df["age"].mean()
print(f"\nAverage age in dataset: {average_age}")
