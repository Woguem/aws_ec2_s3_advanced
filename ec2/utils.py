import os
class Utils:
    def __init__(self):
        # Initialize constants
        self.BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
        self.REGION = os.getenv("AWS_DEFAULT_REGION")  # Default region if not specified
        self.ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
        self.SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    def load_credentials(self):
        """Load AWS credentials from environment variables."""
        if not all([self.ACCESS_KEY, self.SECRET_KEY, self.BUCKET_NAME, self.REGION]):
            raise ValueError("Missing AWS credentials or bucket name. Check your .env file.")
        return self.ACCESS_KEY, self.SECRET_KEY, self.BUCKET_NAME, self.REGION