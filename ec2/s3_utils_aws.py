import os
import boto3


# Optional: define a specific profile if you don't use the "default" profile
# os.environ["AWS_PROFILE"] = "yen"

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

def get_s3_client():
    """Creates and returns an S3 client using AWS profile credentials."""
    return boto3.client("s3") # boto3 is automatically based on ~/.aws/credentials and config

def upload_to_s3(file_path: str, s3_key: str, BUCKET_NAME: str):
    """Uploads a local file to the specified S3 bucket."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local file not found: {file_path}")

        s3 = get_s3_client()
        s3.upload_file(file_path, BUCKET_NAME, s3_key)
        print(f"✅ Uploaded '{file_path}' to S3 as '{s3_key}':'{BUCKET_NAME}/{s3_key}'")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def download_from_s3(s3_key: str, local_path: str, BUCKET_NAME: str):
    """Downloads a file from the specified S3 bucket to a local path."""
    try:
        s3 = get_s3_client()
        s3.download_file(BUCKET_NAME, s3_key, local_path)
        print(f"✅ Downloaded '{BUCKET_NAME}/{s3_key}' from S3 to '{local_path}'")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False
