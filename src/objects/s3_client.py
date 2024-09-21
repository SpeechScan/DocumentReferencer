import os
import boto3
from botocore.client import Config

# Configuration
mode = os.getenv("mode")

bucket_name = os.getenv("s3_bucket")
aws_access_key_id = (
    os.getenv("aws_access_key_id") if mode == "prod" else "minioadmin"
)
aws_secret_access_key = (
    os.getenv("aws_secret_access_key") if mode == "prod" else "minioadmin"
)

# Set endpoint URL only for development mode (MinIO)
endpoint_url = "http://localhost:9000" if mode != "prod" else None

# Initialize boto3 client with optional endpoint URL for MinIO
s3_client = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    config=(
        Config(signature_version="s3v4") if endpoint_url else None
    )
)

if mode != "prod":
    # Check if the bucket exists; if not, create it
    try:
        # Attempt to create the bucket
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        pass
