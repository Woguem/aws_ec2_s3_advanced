import os
import boto3
from dotenv import load_dotenv
from utils import load_env_from_system

# Load credentials from .env file
load_dotenv()
load_env_from_system()

# Initialize constants
'''BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")  # Default region if not specified
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")'''

print(S3_BUCKET_NAME) 
print(AWS_DEFAULT_REGION)


def get_s3_client():
    """Create and return an S3 client using the loaded credentials."""
    if not all([ACCESS_KEY, SECRET_KEY, BUCKET_NAME]):
        raise ValueError("Missing AWS credentials or bucket name. Check your .env file.")

    return boto3.client(
        "s3",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
    )

def upload_to_s3(file_path: str, s3_key: str):
    """Uploads a local file to the specified S3 bucket."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local file not found: {file_path}")

        s3 = get_s3_client()
        s3.upload_file(file_path, BUCKET_NAME, s3_key)
        print(f"✅ Uploaded '{file_path}' to S3 as '{s3_key}'")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def download_from_s3(s3_key: str, local_path: str):
    """Downloads a file from the specified S3 bucket to a local path."""
    try:
        s3 = get_s3_client()
        s3.download_file(BUCKET_NAME, s3_key, local_path)
        print(f"✅ Downloaded '{s3_key}' from S3 to '{local_path}'")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False
