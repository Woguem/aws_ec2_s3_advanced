import os
import boto3
from dotenv import load_dotenv
#from utils import load_env_from_system

# Load environment from system first, then .env file as fallback
def load_env_from_system():
    try:
        # Read from /etc/environment
        with open('/etc/environment', 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    # Strip quotes if present
                    value = value.strip('\'"')
                    os.environ[key] = value
        return True
    except Exception as e:
        print(f"Failed to load environment variables: {e}")
        return False

# Load environment variables
load_env_from_system()
load_dotenv()
#load_env_from_system()

# Initialize constants
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
REGION = os.getenv("AWS_DEFAULT_REGION")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
LAMBDA_NOTIFICATION = os.getenv("ENABLE_LAMBDA_NOTIFICATION", "False").lower() == "true"
LAMBDA_FUNCTION_ARN = os.getenv("LAMBDA_FUNCTION_ARN", "")

# print(os.environ.get("AWS_DEFAULT_REGION"))


def get_s3_client():
    """Create and return an S3 client using the loaded credentials."""
    # Use default region if REGION is empty or None
    region = REGION if REGION and REGION.strip() else "us-east-1"

    try:
        # When running on EC2 with IAM role, boto3 will automatically use instance profile credentials
        if ACCESS_KEY and SECRET_KEY:
            return boto3.client(
                "s3",
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY,
                region_name=region,
            )
        else:
            return boto3.client("s3", region_name=region)
    except Exception as e:
        print(f"Error creating S3 client: {e}")
        raise

def upload_to_s3(file_path: str, s3_key: str):
    """Uploads a local file to the specified S3 bucket."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local file not found: {file_path}")

        s3 = get_s3_client()
        s3.upload_file(file_path, BUCKET_NAME, s3_key)
        print(f"✅ Uploaded '{file_path}' to S3 as '{s3_key}'")

        # Configure Lambda notification if enabled
        if LAMBDA_NOTIFICATION and LAMBDA_FUNCTION_ARN:
            try:
                configure_s3_lambda_trigger(BUCKET_NAME, LAMBDA_FUNCTION_ARN) #type:ignore
                print(f"✅ S3 Lambda trigger configured for bucket {BUCKET_NAME}")
            except Exception as e:
                print(f"⚠️ Failed to configure Lambda trigger: {e}")

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

def configure_s3_lambda_trigger(bucket_name: str, lambda_function_arn: str):
    """Configure S3 to trigger Lambda function on new object creation."""
    try:
        s3 = get_s3_client()

        # Configure bucket notification
        notification_config = {
            'LambdaFunctionConfigurations': [
                {
                    'LambdaFunctionArn': lambda_function_arn,
                    'Events': ['s3:ObjectCreated:*'],
                    'Filter': {
                        'Key': {
                            'FilterRules': [
                                {
                                    'Name': 'suffix',
                                    'Value': '.csv'
                                }
                            ]
                        }
                    }
                }
            ]
        }

        s3.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration=notification_config
        )
        return True
    except Exception as e:
        print(f"Failed to configure S3 Lambda trigger: {e}")
        raise
