import os
import boto3
import shutil

# Configuration
mode = os.getenv("mode")
bucket_name = (
    os.getenv("s3_bucket") if mode == "prod" else "local-bucket"
)  # Local bucket name for non-prod
print(f"BUCKET NAME: {bucket_name}")
aws_access_key_id = os.getenv("aws_access_key_id", "test")
aws_secret_access_key = os.getenv("aws_secret_access_key", "test")

# Initialize file_store based on the mode
if mode == "prod":
    # Use boto3 for production S3
    file_store = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    # Create a wrapper to handle bucket name internally
    class S3Wrapper:
        def __init__(self, client, bucket_name):
            self.client = client
            self.bucket_name = bucket_name

        def upload_file(self, Filename, Key):
            self.client.upload_file(Filename, self.bucket_name, Key)

        def download_file(self, Key, Filename):
            self.client.download_file(self.bucket_name, Key, Filename)

        def delete_object(self, Key):
            self.client.delete_object(Bucket=self.bucket_name, Key=Key)

        def list_objects(self, Prefix=""):
            return self.client.list_objects(Bucket=self.bucket_name, Prefix=Prefix)

    file_store = S3Wrapper(file_store, bucket_name)

else:
    # For local storage, use direct file operations
    local_bucket_path = "./local-file-storage"  # Local storage path
    os.makedirs(local_bucket_path, exist_ok=True)  # Ensure local storage path exists

    # Create a compatible interface to mimic S3 client methods using standard Python libraries
    class LocalFileClient:
        def __init__(self, bucket_path):
            self.bucket_path = bucket_path

        def upload_file(self, Filename, Key):
            # Save file to local storage path
            destination = os.path.join(self.bucket_path, Key)
            os.makedirs(
                os.path.dirname(destination), exist_ok=True
            )  # Create any necessary directories
            shutil.copy(Filename, destination)
            print(f"Uploaded to local path: {destination}")

        def download_file(self, Key, Filename):
            # Retrieve file from local storage path
            source = os.path.join(self.bucket_path, Key)
            if not os.path.exists(source):
                raise FileNotFoundError(f"The file {source} does not exist.")
            shutil.copy(source, Filename)
            print(f"Downloaded from local path: {source}")

        def delete_object(self, Key):
            # Remove file from local storage path
            file_path = os.path.join(self.bucket_path, Key)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted local file: {file_path}")
            else:
                print(f"File not found for deletion: {file_path}")

        def list_objects(self, Prefix=""):
            # List files in local storage matching the Prefix
            matched_files = []
            for root, _, files in os.walk(self.bucket_path):
                for file in files:
                    relative_path = os.path.relpath(
                        os.path.join(root, file), self.bucket_path
                    )
                    if relative_path.startswith(Prefix):
                        matched_files.append({"Key": relative_path})
            print(f"Listed objects with prefix '{Prefix}': {matched_files}")
            return {"Contents": matched_files}

    # Instantiate the LocalFileClient for local file handling
    file_store = LocalFileClient(local_bucket_path)
