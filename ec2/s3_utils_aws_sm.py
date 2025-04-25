import os
import boto3
from botocore.exceptions import ClientError
import json

def get_secret():
    """Retrieve secrets from AWS Secrets Manager."""
    secret_name = "secret_for_my_api"
    region_name = "eu-west-3"

    # Create a Secrets Manager client
    client = boto3.client("secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response["SecretString"])
        return secret
    except ClientError as e:
        print(f"❌ Failed to retrieve secret: {e}")
        raise 

# 🔐 Recover credentials from Secrets Manager

secrets = get_secret()

AWS_ACCESS_KEY = secrets["AWS_ACCESS_KEY_ID"].replace("\"", "")
AWS_SECRET_KEY = secrets["AWS_SECRET_ACCESS_KEY"].replace("\"", "")
AWS_REGION = secrets["AWS_DEFAULT_REGION"].replace("\"", "")  
BUCKET_NAME = secrets["S3_BUCKET_NAME"].replace("\"", "") 


def get_s3_client():
    """Creates and returns an S3 client using secrets-based credentials."""
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
def upload_to_s3(file_path: str, s3_key: str):
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

def download_from_s3(s3_key: str, local_path: str):
    """Downloads a file from the specified S3 bucket to a local path."""
    try:
        s3 = get_s3_client()
        s3.download_file(BUCKET_NAME, s3_key, local_path)
        print(f"✅ Downloaded '{BUCKET_NAME}/{s3_key}' from S3 to '{local_path}'")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False
