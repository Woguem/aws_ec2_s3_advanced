import json
import urllib.parse
import os
import requests

# Configuration
API_ENDPOINT = os.environ.get('API_ENDPOINT', 'http://ec2-fastapi-server:8000')
MODEL_TYPE = os.environ.get('MODEL_TYPE', 'random_forest')  # Default model type

def lambda_handler(event, context):
    # Get the bucket name and key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    print(f"Processing new data upload: {key} in bucket {bucket}")

    try:
        # Call the retrain endpoint of your FastAPI service
        response = requests.post(f"{API_ENDPOINT}/retrain?model_type={MODEL_TYPE}")

        if response.status_code == 200:
            print(f"Model retraining successful: {response.json()}")
            return {
                'statusCode': 200,
                'body': json.dumps(f'Successfully retrained model using {key}')
            }
        else:
            print(f"Error during retraining: {response.text}")
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error retraining model: {response.text}')
            }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing S3 event: {str(e)}')
        }
