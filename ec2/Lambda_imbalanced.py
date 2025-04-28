import json
import urllib.parse
import os
import requests
import pandas as pd
from sklearn.utils import resample
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler
import boto3
from s3_utils_aws_sm import download_from_s3, upload_to_s3


# Configuration
API_ENDPOINT = os.environ.get('API_ENDPOINT', 'http://13.38.30.107:8000')
MODEL_TYPE = os.environ.get('MODEL_TYPE', 'random_forest')  # Default model type

def balance_data(data):
    """Balance the data using SMOTE or other techniques."""
    
    # Separate features and target variable
    X = data.drop('target', axis=1)
    y = data['target']
    
    # Appy SMOTE to balance the dataset
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X, y)
    
    # Recreate the DataFrame with balanced data
    balanced_data = pd.DataFrame(X_res, columns=X.columns)
    balanced_data['target'] = y_res
    
    print(f"Balanced class distribution: {balanced_data['target'].value_counts()}")
    
    return balanced_data

def lambda_handler(event, context):
    # Get the bucket name and key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    print(f"Processing new data upload: {key} in bucket {bucket}")

    try:
        # Download the file from S3
        download_from_s3(key, '/tmp/data.csv')
        
        # Load csv file into a DataFrame
        data = pd.read_csv('/tmp/data.csv')

        # Verify the class distribution before balancing
        class_counts = data['target'].value_counts()
        print(f"Class distribution before balancing: \n{class_counts}")

        if class_counts.min() < class_counts.max():
            print("Data is imbalanced. Balancing data...")
        
            # Apply data balancing techniques
            balanced_data = balance_data(data)
        
            # Save the balanced data to a temporary location
            balanced_data.to_csv('/tmp/balanced_data.csv', index=False)

        else:
            print("Data is already balanced.")
            balanced_data = data

        # Upload the balanced data back to S3
        upload_to_s3('/tmp/balanced_data.csv', 'balanced_data.csv')
        
        # Send the balanced data to the FastAPI service for retraining
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
