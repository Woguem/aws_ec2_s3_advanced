# lambda_function.py
import boto3
import json
from datetime import datetime

from sagemaker import image_uris

# Get the URI for the built-in XGBoost image
image_uri = image_uris.retrieve(
    framework='xgboost',
    region='eu-west-3',
    version='1.5-1'
)

def lambda_handler(event, context):
    # Initialize clients
    sagemaker = boto3.client('sagemaker')
    s3 = boto3.client('s3')
    
    # Get bucket and key from event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Create training job name
    job_name = f"training-job-{datetime.now().strftime('%Y%m%d%H%M%S')}"
# Start training job
    response = sagemaker.create_training_job(
        TrainingJobName=job_name,
        AlgorithmSpecification={
            'TrainingImage': 'image_uri',
            'TrainingInputMode': 'File'
        },
        RoleArn='arn:aws:iam::556417283723:role/accesss3',
        InputDataConfig=[
            {
                'ChannelName': 'train',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': f's3://{bucket}/{key}',
                        'S3DataDistributionType': 'FullyReplicated'
                    }
                }
            }
        ],
        OutputDataConfig={
            'S3OutputPath': 's3://{bucket}/training_model/'
        },
        ResourceConfig={
            'InstanceType': 'ml.m4.xlarge',
            'InstanceCount': 1,
            'VolumeSizeInGB': 30
        },
        StoppingCondition={
            'MaxRuntimeInSeconds': 3600
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Started training job: {job_name}')
    }

